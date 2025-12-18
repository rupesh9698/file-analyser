import chainlit as cl
import pandas as pd
import docx
from pptx import Presentation
import os
import json
from bs4 import BeautifulSoup
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import PyMuPDFLoader, BSHTMLLoader

# Disable telemetry
os.environ["CHAINLIT_TELEMETRY_ENABLED"] = "false"

# Initialize LLM
try:
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=os.environ.get("GOOGLE_API_KEY"),
        temperature=0.3,
    )
except Exception as e:
    llm = None
    print(f"LLM initialization error: {e}")

# Supported languages
LANGUAGES = [
    "English", "Spanish", "French", "German", "Italian", "Portuguese",
    "Russian", "Chinese (Simplified)", "Japanese", "Korean",
    "Arabic", "Hindi", "Turkish", "Dutch"
]

@cl.on_chat_start
async def start():
    if not llm:
        await cl.Message(content="Error: `GOOGLE_API_KEY` is not set or invalid. Please configure it in Secrets.").send()
        return

    await cl.Message(
        content="Hello! Upload a file (CSV, XLSX, DOCX, PDF, PPTX, TXT, HTML, XML, JSON) to analyze or translate."
    ).send()

    files = await cl.AskFileMessage(
        content="Please upload a file:",
        accept=[
            "text/csv",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "text/plain",
            "text/html",
            "text/xml", "application/xml",
            "application/json",
        ],
        max_size_mb=20,
        timeout=300,
    ).send()

    if not files:
        await cl.Message(content="No file uploaded. Restart the chat to try again.").send()
        return

    file = files[0]
    cl.user_session.set("file_name", file.name)

    msg = cl.Message(content=f"Processing `{file.name}`...")
    await msg.send()

    try:
        if file.type in ["text/csv", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]:
            df = pd.read_csv(file.path) if file.type == "text/csv" else pd.read_excel(file.path)
            cl.user_session.set("data", df)
            cl.user_session.set("file_type", "csv")
            msg.content = f"✅ `{file.name}` loaded as tabular data.\nYou can ask questions or translate specific text."
        else:
            full_text = ""
            if file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                document = docx.Document(file.path)
                full_text = "\n".join([p.text for p in document.paragraphs if p.text.strip()])

            elif file.type == "application/pdf":
                loader = PyMuPDFLoader(file.path)
                pages = loader.load()
                full_text = "\n".join([page.page_content for page in pages])

            elif file.type == "application/vnd.openxmlformats-officedocument.presentationml.presentation":
                prs = Presentation(file.path)
                text_runs = []
                for slide in prs.slides:
                    for shape in slide.shapes:
                        if hasattr(shape, "has_text_frame") and shape.has_text_frame:
                            for paragraph in shape.text_frame.paragraphs:
                                if paragraph.text.strip():
                                    text_runs.append(paragraph.text)
                full_text = "\n".join(text_runs)

            elif file.type == "text/plain":
                with open(file.path, "r", encoding="utf-8") as f:
                    full_text = f.read()

            elif file.type == "text/html":
                loader = BSHTMLLoader(file.path, open_encoding="utf-8")
                docs = loader.load()
                full_text = "\n".join([doc.page_content for doc in docs])

            elif file.type in ["text/xml", "application/xml"]:
                with open(file.path, "r", encoding="utf-8") as f:
                    content = f.read()
                soup = BeautifulSoup(content, "xml")
                full_text = soup.get_text(separator="\n", strip=True)

            elif file.type == "application/json":
                with open(file.path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                full_text = json.dumps(data, indent=2, ensure_ascii=False)

            cl.user_session.set("data", full_text)
            cl.user_session.set("file_type", "text")
            msg.content = f"✅ `{file.name}` loaded as text.\nYou can ask questions or translate content."

        await msg.update()

        # Add Translate button
        await cl.Message(
            content="What would you like to do next?",
            actions=[
                cl.Action(
                    name="translate",
                    label="🌐 Translate",
                    payload={"trigger": "translate"}
                )
            ]
        ).send()

    except Exception as e:
        await cl.Message(content=f"Error processing file: {str(e)}").send()


@cl.action_callback("translate")
async def on_translate_action(action: cl.Action):
    data = cl.user_session.get("data")
    file_type = cl.user_session.get("file_type")

    # Select target language
    lang_actions = [
        cl.Action(name=lang, label=lang, payload={"lang": lang}) for lang in LANGUAGES
    ]
    lang_res = await cl.AskActionMessage(
        content="Select target language:",
        actions=lang_actions
    ).send()

    if not lang_res:
        await cl.Message(content="Translation cancelled.").send()
        return

    target_lang = lang_res.get("payload", {}).get("lang", "English")

    # Decide what to translate
    if file_type == "text" and isinstance(data, str) and len(data.strip()) > 0:
        choice_res = await cl.AskActionMessage(
            content="What do you want to translate?",
            actions=[
                cl.Action(name="full", label="📄 Entire document", payload={"choice": "full"}),
                cl.Action(name="custom", label="✍️ Custom text", payload={"choice": "custom"})
            ]
        ).send()

        if not choice_res:
            await cl.Message(content="Translation cancelled.").send()
            return

        choice = choice_res.get("payload", {}).get("choice")

        if choice == "custom":
            text_msg = await cl.AskUserMessage(content="Enter the text to translate:", timeout=300).send()
            if not text_msg:
                await cl.Message(content="Translation cancelled.").send()
                return
            text_to_translate = text_msg["output"]
        else:
            text_to_translate = data
            if len(text_to_translate) > 10000:
                await cl.Message(content="Document too long. Translating first 10,000 characters...").send()
                text_to_translate = text_to_translate[:10000]
    else:
        # CSV or no text → force custom
        text_msg = await cl.AskUserMessage(content="Enter the text to translate:", timeout=300).send()
        if not text_msg:
            await cl.Message(content="Translation cancelled.").send()
            return
        text_to_translate = text_msg["output"]

    translating_msg = cl.Message(content=f"Translating to **{target_lang}**...")
    await translating_msg.send()

    try:
        if not llm:
            raise Exception("LLM not available")

        prompt = ChatPromptTemplate.from_template(
            """Translate the following text to {target_lang} naturally and accurately.
            Preserve formatting (lists, headings, etc.) as much as possible.

            Text:
            {text}

            Translation:"""
        )

        chain = prompt | llm | StrOutputParser()
        response = await chain.ainvoke({
            "target_lang": target_lang,
            "text": text_to_translate
        })

        translating_msg.content = f"**Translation to {target_lang}:**\n\n{response}"
        await translating_msg.update()

    except Exception as e:
        translating_msg.content = f"Translation failed: {str(e)}"
        await translating_msg.update()


@cl.on_message
async def main(message: cl.Message):
    data = cl.user_session.get("data")
    file_type = cl.user_session.get("file_type")

    if not data or not llm:
        await cl.Message(content="Please upload a file first.").send()
        return

    thinking = cl.Message(content="Thinking...")
    await thinking.send()

    try:
        if file_type == "csv" and isinstance(data, pd.DataFrame):
            df_info = f"Rows: {data.shape[0]}, Columns: {data.shape[1]}\nColumns: {list(data.columns)}\nSample:\n{data.head(3).to_string()}"

            prompt = ChatPromptTemplate.from_template(
                """You are a data analyst. Answer based only on the dataset.

                Dataset info:
                {df_info}

                Question: {question}

                Answer clearly."""
            )
            chain = prompt | llm | StrOutputParser()
            response = await chain.ainvoke({
                "df_info": df_info,
                "question": message.content
            })

        else:
            context = str(data)[:6000]
            prompt = ChatPromptTemplate.from_template(
                """Answer the question using only the provided document content.

                Content:
                {context}

                Question: {question}

                If unsure, say "I don't know based on the document." """
            )
            chain = prompt | llm | StrOutputParser()
            response = await chain.ainvoke({
                "context": context,
                "question": message.content
            })

        thinking.content = response
        await thinking.update()

    except Exception as e:
        thinking.content = f"Error: {str(e)}"
        await thinking.update()