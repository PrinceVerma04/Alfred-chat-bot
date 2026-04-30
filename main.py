"""Alfred chatbot CLI entry point."""

import argparse
import logging
import sys

from dotenv import load_dotenv

load_dotenv()

from src.chatbot import create_chatbot
from src.config import COMPANY_NAME, COMPANY_URL, FAISS_INDEX_PATH, SCRAPED_DATA_PATH
from src.scraper import WebScraper
from src.vector_store import create_vector_store

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def scrape_command(args):
    """Scrape the company website and create a local FAISS vector store."""
    logger.info("Starting web scraping...")

    try:
        scraper = WebScraper(url=args.url, max_pages=args.max_pages)
        documents = scraper.scrape()

        if not documents:
            print("Error: no documents were scraped. Please check the URL.")
            return 1

        create_vector_store(documents)

        print(f"\nOK: scraped {len(documents)} pages from {args.url}")
        print(f"Raw scraped data: {SCRAPED_DATA_PATH}")
        print(f"Local FAISS index: {FAISS_INDEX_PATH}")
        print("Next: python main.py --chat")
        return 0

    except Exception as exc:
        logger.error("Error during scraping: %s", exc)
        print(f"Error: {exc}")
        return 1


def chat_command(args):
    """Start an interactive chat session."""
    logger.info("Starting chat session...")

    try:
        chatbot = create_chatbot()

        print("\n" + "=" * 50)
        print(f"{COMPANY_NAME} Chatbot")
        print("=" * 50)
        print("Type 'exit' or 'quit' to end the session")
        print("Type 'clear' to clear chat history")
        print("=" * 50 + "\n")

        while True:
            try:
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in {"exit", "quit", "q"}:
                    print("\nGoodbye!")
                    break

                if user_input.lower() == "clear":
                    chatbot.clear_history()
                    print("Chat history cleared.")
                    continue

                response = chatbot.chat(user_input)
                print(f"\nAI: {response['answer']}")

                if response["sources"] and args.verbose:
                    print("\nSources:")
                    for index, source in enumerate(response["sources"], 1):
                        metadata = source["metadata"]
                        title = metadata.get("title", "Unknown")
                        url = metadata.get("url", "")
                        print(f"  {index}. {title} - {url}")

                print()

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as exc:
                print(f"Error: {exc}")

        return 0

    except Exception as exc:
        logger.error("Error during chat: %s", exc)
        print(f"Error: {exc}")
        print("\nMake sure you have added OPENAI_API_KEY to .env and run `python main.py --scrape` first.")
        return 1


def build_parser():
    """Build CLI parser supporting flags and subcommands."""
    parser = argparse.ArgumentParser(
        description="Alfred Lab chatbot using LangChain with local FAISS storage"
    )
    parser.add_argument("--scrape", action="store_true", help="Scrape the company website and build local FAISS")
    parser.add_argument("--chat", action="store_true", help="Start an interactive chat session")
    parser.add_argument("--url", default=COMPANY_URL, help="Company website URL to scrape")
    parser.add_argument("--max-pages", type=int, default=20, help="Maximum number of internal pages to scrape")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show source documents in chat")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    scrape_parser = subparsers.add_parser("scrape", help="Scrape company website and create vector store")
    scrape_parser.add_argument("--url", default=COMPANY_URL, help="Company website URL to scrape")
    scrape_parser.add_argument("--max-pages", type=int, default=20, help="Maximum number of internal pages to scrape")
    scrape_parser.set_defaults(func=scrape_command)

    chat_parser = subparsers.add_parser("chat", help="Start interactive chat session")
    chat_parser.add_argument("-v", "--verbose", action="store_true", help="Show source documents")
    chat_parser.set_defaults(func=chat_command)

    return parser


def main():
    """Main entry point."""
    parser = build_parser()
    args = parser.parse_args()

    if args.scrape and args.chat:
        parser.error("Choose either --scrape or --chat, not both.")

    if args.scrape:
        args.func = scrape_command
    elif args.chat:
        args.func = chat_command
    elif args.command is None:
        args.func = chat_command

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
