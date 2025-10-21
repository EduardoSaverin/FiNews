from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from typing import TypedDict, Any
from dotenv import load_dotenv
import re

if load_dotenv():
    print("✅ .env loaded")

# State
class ArticleState(TypedDict):
    text: str
    cleaned_text: str
    summary: str

# Models
cleaner_model = ChatGroq(model="deepseek-r1-distill-llama-70b", temperature=0)
summarizer_model = ChatGroq(model="deepseek-r1-distill-llama-70b", temperature=0.3)

def extract_text(result: Any) -> str:
    """
    Extracts clean text from LangChain model.invoke() result,
    safely handling both string and structured list responses.
    """
    content = getattr(result, "content", None)
    if content is None:
        return ""

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, dict):
                text_part = block.get("text")
                if isinstance(text_part, str):
                    parts.append(text_part)
            elif hasattr(block, "text"):
                text_part = getattr(block, "text", "")
                if isinstance(text_part, str):
                    parts.append(text_part)
        return " ".join(parts).strip()

    return str(content).strip()

def clean_article(state: ArticleState) -> ArticleState:
    text = state["text"]
    prompt = f"""
    You are a news content cleaner. Your task is to remove all unrelated parts
    from the following article text, such as:
    - 'Also Read', 'Follow us on', 'Read more', or 'Subscribe' lines
    - Author bios or contact details
    - Repeated headlines or unrelated news items

    Keep only the main article body in natural language form.

    --- ARTICLE START ---
    {text}
    --- ARTICLE END ---
    """
    result = cleaner_model.invoke(prompt)
    cleaned_text = extract_text(result)
    state["cleaned_text"] = cleaned_text
    return state


def summarize_article(state: ArticleState) -> ArticleState:
    combined_text: str = state.get("cleaned_text", "")
    """
    Takes cleaned articles, merges them, and generates a concise daily summary
    of FinTech updates for WhatsApp broadcast.
    """

    prompt = f"""
    You are a financial news summarizer for an Indian FinTech daily.
    Summarize the key takeaways from the following cleaned articles into:
    - 5 crisp bullet points
    - Cover only FinTech, banking, UPI, RBI, startups, or payments topics
    - Avoid repetition or minor stories
    - Keep tone: informative + professional
    
    --- CLEANED ARTICLES START ---
    {combined_text}
    --- CLEANED ARTICLES END ---
    """

    result = summarizer_model.invoke(prompt)
    summary_text = extract_text(result)
    state["summary"] = summary_text
    return state

def remove_thought_tags(state: ArticleState) -> ArticleState:
    cleaned_text = state["cleaned_text"]
    if not cleaned_text:
        return state
    # Remove <think>...</think> completely
    cleaned = re.sub(r"<think>.*?</think>", "", cleaned_text, flags=re.DOTALL|re.IGNORECASE)

    # Optionally remove other unwanted tags, e.g., <reason>...</reason>
    cleaned = re.sub(r"<.*?>", "", cleaned)

    # Collapse multiple spaces
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    state["cleaned_text"] = cleaned

    return state

def build_graph():
    graph = StateGraph(ArticleState)

    # Nodes
    graph.add_node("clean_article", clean_article)
    graph.add_node("summarize_article", summarize_article)
    graph.add_node("tag_remover", remove_thought_tags)

    # Edges
    graph.add_edge(START, "clean_article")
    graph.add_edge("clean_article", "tag_remover")
    graph.add_edge("tag_remover", END)

    return graph.compile()