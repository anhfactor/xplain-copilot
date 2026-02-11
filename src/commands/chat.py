"""Interactive chat mode module."""

import typer
from typing import Optional
from typing_extensions import Annotated

from ..core import (
    chat_with_copilot,
    print_banner,
    print_explanation,
    print_error,
    print_info,
    print_success,
    LoadingSpinner,
    format_language_flag,
    console,
    CopilotCLIError,
)
from ..core.history_store import history as history_store
from ..config import config, LANGUAGE_NAMES

def print_chat_help():
    """Print chat mode help."""
    help_text = """
[bold cyan]Available Commands:[/]
  [yellow]/help[/]     - Show this help message
  [yellow]/lang XX[/]  - Change language (e.g., /lang vi)
  [yellow]/clear[/]    - Clear conversation history
  [yellow]/exit[/]     - Exit chat mode
  [yellow]/quit[/]     - Exit chat mode

[bold cyan]Tips:[/]
  • Ask about code, commands, errors, or any dev topic
  • Context is maintained across messages
  • Use clear, specific questions for best results
"""
    console.print(help_text)


def chat(
    lang: Annotated[
        Optional[str],
        typer.Option("--lang", "-l", help="Output language (en, vi, zh, ja, ko, es, fr, de, pt, ru)")
    ] = None,
):
    """
    Start an interactive chat session with GitHub Copilot.
    
    Examples:
        xplain chat
        xplain chat --lang vi
    """
    # Use provided language or fall back to config
    output_lang = lang or config.language
    
    # Validate language
    if output_lang not in LANGUAGE_NAMES:
        print_error(
            f"Unsupported language: {output_lang}\n"
            f"Supported: {', '.join(LANGUAGE_NAMES.keys())}"
        )
        raise typer.Exit(1)
    
    # Print welcome banner
    print_banner()
    print_info(f"Interactive Chat Mode {format_language_flag(output_lang)} {LANGUAGE_NAMES[output_lang]}")
    print_info("Type [yellow]/help[/] for commands, [yellow]/exit[/] to quit\n")
    
    # Conversation history
    history: list[dict] = []
    
    while True:
        try:
            # Get user input
            console.print("[bold green]You>[/] ", end="")
            user_input = input().strip()
            
            if not user_input:
                continue
            
            # Handle special commands
            if user_input.startswith("/"):
                cmd = user_input.lower().split()[0]
                
                if cmd in ("/exit", "/quit", "/q"):
                    print_success("Goodbye! Happy coding! 🚀")
                    break
                
                elif cmd == "/help":
                    print_chat_help()
                    continue
                
                elif cmd == "/clear":
                    history.clear()
                    print_success("Conversation history cleared")
                    continue
                
                elif cmd == "/lang":
                    parts = user_input.split()
                    if len(parts) < 2:
                        print_info(f"Current language: {format_language_flag(output_lang)} {LANGUAGE_NAMES[output_lang]}")
                        print_info(f"Available: {', '.join(LANGUAGE_NAMES.keys())}")
                    else:
                        new_lang = parts[1].lower()
                        if new_lang in LANGUAGE_NAMES:
                            output_lang = new_lang
                            print_success(f"Language changed to {format_language_flag(output_lang)} {LANGUAGE_NAMES[output_lang]}")
                        else:
                            print_error(f"Unknown language: {new_lang}")
                            print_info(f"Available: {', '.join(LANGUAGE_NAMES.keys())}")
                    continue
                
                else:
                    print_error(f"Unknown command: {cmd}")
                    print_info("Type /help for available commands")
                    continue
            
            # Add to history
            history.append({"role": "user", "content": user_input})
            
            # Get response from Copilot
            try:
                with LoadingSpinner("Thinking..."):
                    response = chat_with_copilot(
                        user_input,
                        history,
                        LANGUAGE_NAMES[output_lang]
                    )
                
                # Add response to history
                history.append({"role": "assistant", "content": response})
                
                # Save to persistent history
                history_store.add("chat", user_input, response, language=output_lang)
                
                # Display response
                console.print()
                print_explanation(
                    response,
                    title="Copilot",
                    subtitle=None
                )
                console.print()
                
            except CopilotCLIError as e:
                print_error(str(e))
                # Remove the failed user message from history
                history.pop()
                continue
        
        except KeyboardInterrupt:
            console.print()
            print_success("Goodbye! Happy coding! 🚀")
            break
        
        except EOFError:
            console.print()
            print_success("Goodbye! Happy coding! 🚀")
            break
