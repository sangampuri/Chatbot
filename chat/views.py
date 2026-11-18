import logging

import markdown
import nh3
from django.conf import settings
from django.shortcuts import render, redirect
from groq import Groq

from .forms import ChatForm
from .models import Chat

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = "You are a helpful assistant."
HISTORY_LIMIT = 5


def _get_ai_response(user_message, previous_chats):
    """Build the message list, call Groq, return sanitized HTML."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for chat in reversed(previous_chats):
        messages.append({"role": "user", "content": chat.user_message})
        messages.append({"role": "assistant", "content": chat.ai_response})

    # Current message is appended ONCE, outside the loop.
    messages.append({"role": "user", "content": user_message})

    try:
        client = Groq(api_key=settings.GROQ_API_KEY)

        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            max_tokens=500,
        )

        raw_content = response.choices[0].message.content or ""

        # Markdown -> HTML, then sanitize.
        ai_html = markdown.markdown(
            raw_content,
            extensions=["tables", "fenced_code"],
        )

        ai_html = nh3.clean(
            ai_html,
            tags=nh3.ALLOWED_TAGS
            | {
                "table", "thead", "tbody", "tr", "th", "td",
                "pre", "code", "hr", "br",
            },
            attributes={
                "*": {"class"},
                "a": {"href", "title"},
                "code": {"class"},
            },
        )
        return ai_html

    except Exception:
        logger.exception("Groq API error")
        return (
            "Sorry! I'm unable to generate a response right now. "
            "Please try again."
        )


def chat_view(request):
    # Create a session if the visitor doesn't have one.
    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    form = ChatForm()

    if request.method == "POST":
        form = ChatForm(request.POST)

        if form.is_valid():
            user_message = form.cleaned_data["user_message"]

            # Only this visitor's last N conversations.
            previous_chats = list(
                Chat.objects.filter(session_key=session_key)
                .order_by("-created_at")[:HISTORY_LIMIT]
            )

            ai_response = _get_ai_response(user_message, previous_chats)

            chat = form.save(commit=False)
            chat.session_key = session_key
            chat.ai_response = ai_response
            chat.save()

            return redirect("chat")

    chats = (
        Chat.objects.filter(session_key=session_key)
        .order_by("created_at")
    )

    return render(
        request,
        "chat/chat.html",
        {"form": form, "chats": chats},
    )