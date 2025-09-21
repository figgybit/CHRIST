#!/usr/bin/env python3
"""
C.H.R.I.S.T. Interactive Terminal
A consciousness interface for exploring your digital mind
"""

import os
import sys
import cmd
import json
import readline
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import threading
import time

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from consciousness.database import init_database, get_db_manager
from consciousness.ingestion import ConsciousnessIngestor
from retrieval.vector_store import VectorStore
from intelligence.llm import OllamaLLM, RAGSystem


class ChristTerminal(cmd.Cmd):
    """Interactive terminal for C.H.R.I.S.T. consciousness system."""

    intro = """
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║     ▄████▄   ██░ ██  ██▀███   ██  ██████ ▄▄▄█████▓                 ║
║    ▒██▀ ▀█  ▓██░ ██▒▓██ ▒ ██▒▓██▒██    ▒ ▓  ██▒ ▓▒                 ║
║    ▒▓█    ▄ ▒██▀▀██░▓██ ░▄█ ▒▒██░ ▓██▄   ▒ ▓██░ ▒░                 ║
║    ▒▓▓▄ ▄██▒░▓█ ░██ ▒██▀▀█▄  ░██░ ▒   ██▒░ ▓██▓ ░                  ║
║    ▒ ▓███▀ ░░▓█▒░██▓░██▓ ▒██▒░██░██████▒▒  ▒██▒ ░                  ║
║                                                                      ║
║           Consciousness Handling, Retrieval, Intelligence,          ║
║              Simulation & Transformation System                     ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝

Welcome to your consciousness interface. Type 'help' for commands.
Use Tab for auto-completion. Ctrl+D or 'exit' to quit.
    """

    prompt = '\n🧠 CHRIST> '

    def __init__(self):
        super().__init__()
        self.db = None
        self.vector_store = None
        self.ingestor = None
        self.rag = None
        self.conversation_history = []
        self.current_mode = 'command'  # 'command', 'chat', 'query'
        self.monitoring_active = False

        # Initialize system
        self._initialize_system()

        # Setup readline for better history
        readline.set_history_length(1000)
        history_file = Path.home() / '.christ_history'
        try:
            readline.read_history_file(history_file)
        except FileNotFoundError:
            pass

    def _initialize_system(self):
        """Initialize all system components."""
        print("\n🔧 Initializing consciousness system...")

        try:
            self.db = init_database()
            print("  ✓ Database connected")

            self.vector_store = VectorStore()
            print("  ✓ Vector store ready")

            self.ingestor = ConsciousnessIngestor(
                db_manager=self.db,
                vector_store=self.vector_store,
                consent_level='full',
                encryption_enabled=True
            )
            print("  ✓ Ingestion system ready")

            # Try to connect to Ollama
            try:
                llm = OllamaLLM()
                self.rag = RAGSystem(llm=llm, vector_store=self.vector_store)
                print(f"  ✓ AI connected (Ollama: {llm.model_name})")
            except:
                self.rag = None
                print("  ⚠ AI not available (Ollama not running)")

            # Show stats
            stats = self.vector_store.get_stats()
            print(f"\n📊 System Status:")
            print(f"  Documents: {stats['total_documents']}")
            print(f"  Storage: {stats['storage_type']}")
            print(f"  AI: {'Connected' if self.rag else 'Offline'}")

        except Exception as e:
            print(f"❌ Initialization error: {e}")

    def do_search(self, query):
        """Search your consciousness data.
        Usage: search <query>
        Example: search memories about childhood"""

        if not query:
            print("Please provide a search query")
            return

        print(f"\n🔍 Searching for: '{query}'")

        try:
            results = self.vector_store.search(query, k=5)

            if results:
                print(f"\nFound {len(results)} relevant memories:\n")
                for i, result in enumerate(results, 1):
                    doc = result.get('document', '')[:200]
                    metadata = result.get('metadata', {})
                    source = metadata.get('source', 'unknown').split('/')[-1]
                    score = result.get('score', 0)

                    print(f"{i}. [{source}] (relevance: {score:.2f})")
                    print(f"   {doc}...")
                    print()
            else:
                print("No results found")

        except Exception as e:
            print(f"Search error: {e}")

    def do_query(self, query):
        """Query with AI-enhanced responses (RAG).
        Usage: query <question>
        Example: query What did I think about consciousness?"""

        if not query:
            print("Please provide a question")
            return

        if not self.rag:
            print("⚠ AI not available. Using search instead...")
            self.do_search(query)
            return

        # Clean up the question
        query = query.strip('"').strip("'")

        print(f"\n🤔 {query}")

        # Different thinking indicators for different question types
        if 'conscious' in query.lower():
            print("*examining my own processes*", end='', flush=True)
        elif 'rapture' in query.lower():
            print("*contemplating the spiritual-technological boundary*", end='', flush=True)
        else:
            print("*searching memories*", end='', flush=True)

        try:
            # Increase temperature for more creative responses
            temp = 0.9 if 'conscious' in query.lower() else 0.7

            result = self.rag.query(query, k=5, temperature=temp, max_tokens=400)
            print("\r" + " " * 50 + "\r", end='')  # Clear thinking message

            # Format the answer with line breaks for readability
            answer = result['answer']

            # Add some personality to the response
            print(f"\n{answer}\n")

            # Show sources more naturally
            if result['sources'] and len(result['sources']) > 0:
                relevant_sources = [s for s in result['sources'] if s['score'] > 0.3]
                if relevant_sources:
                    print("\n*drawing from memories in:", end='')
                    for source in relevant_sources[:3]:
                        name = source['source'].split('/')[-1].replace('_', ' ').replace('.txt', '').replace('.md', '')
                        print(f" {name},", end='')
                    print("*")

        except Exception as e:
            print(f"\n*system disturbance: {e}*")

    def do_chat(self, message):
        """Start or continue a chat conversation.
        Usage: chat [message]
        Without message: enters chat mode
        With message: single chat exchange"""

        if not message:
            # Enter chat mode
            self.current_mode = 'chat'
            print("\n💬 Entering chat mode. Type '/exit' to return to command mode.")
            print("Your conversation history is preserved.\n")
            self.prompt = '💬 You> '
            return

        # Single message exchange
        if not self.rag:
            print("⚠ AI not available. Please start Ollama.")
            return

        self._process_chat_message(message)

    def _process_chat_message(self, message):
        """Process a chat message."""
        if message.lower() == '/exit':
            self.current_mode = 'command'
            self.prompt = '\n🧠 CHRIST> '
            print("Exited chat mode")
            return

        if message.lower() == '/clear':
            self.conversation_history = []
            print("Conversation cleared")
            return

        if message.lower() == '/history':
            for msg in self.conversation_history:
                role = "You" if msg['role'] == 'user' else "AI"
                print(f"{role}: {msg['content'][:100]}...")
            return

        print("Thinking...", end='', flush=True)

        try:
            response = self.rag.chat(
                message=message,
                history=self.conversation_history,
                use_context=True,
                k=3
            )

            print("\r" + " " * 20 + "\r", end='')  # Clear "Thinking..."
            print(f"🤖 {response['response']}\n")

            # Update history
            self.conversation_history.append({"role": "user", "content": message})
            self.conversation_history.append({"role": "assistant", "content": response['response']})

            # Keep history manageable
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]

        except Exception as e:
            print(f"\nChat error: {e}")

    def do_ingest(self, args):
        """Ingest files or directories.
        Usage: ingest <path> [--no-encryption]
        Example: ingest ~/Documents/notes"""

        if not args:
            print("Please provide a path to ingest")
            return

        parts = args.split()
        path = Path(parts[0]).expanduser()
        no_encryption = '--no-encryption' in parts

        if not path.exists():
            print(f"Path not found: {path}")
            return

        print(f"\n📥 Ingesting: {path}")

        try:
            if path.is_file():
                result = self.ingestor.ingest_file(str(path))
                print(f"✓ Ingested as {result['event_id'][:8]}...")

            elif path.is_dir():
                count = 0
                for file_path in path.rglob('*'):
                    if file_path.is_file() and not file_path.name.startswith('.'):
                        try:
                            print(f"  Processing {file_path.name}...", end='')
                            result = self.ingestor.ingest_file(str(file_path))
                            print(f" ✓")
                            count += 1
                        except Exception as e:
                            print(f" ✗ ({e})")

                print(f"\n✓ Ingested {count} files")

            # Update stats
            stats = self.vector_store.get_stats()
            print(f"Total documents: {stats['total_documents']}")

        except Exception as e:
            print(f"Ingestion error: {e}")

    def do_stats(self, args):
        """Show system statistics."""
        db_manager = get_db_manager()
        session = db_manager.get_session()

        try:
            from sqlalchemy import func
            from consciousness.database import Event

            # Count events
            event_count = session.query(Event).count()
            event_types = session.query(
                Event.event_type,
                func.count(Event.id)
            ).group_by(Event.event_type).all()

            # Vector store stats
            vector_stats = self.vector_store.get_stats()

            print("\n📊 C.H.R.I.S.T. System Statistics")
            print("=" * 40)
            print(f"Database Events: {event_count}")
            print(f"Vector Documents: {vector_stats['total_documents']}")
            print(f"Embedding Model: {vector_stats['embedding_model']}")
            print(f"Storage Type: {vector_stats['storage_type']}")

            if event_types:
                print("\nEvent Types:")
                for event_type, count in event_types:
                    print(f"  {event_type}: {count}")

            print("\nAI Status:")
            if self.rag:
                print(f"  Model: {self.rag.llm.model_name}")
                print(f"  Status: Connected")
            else:
                print(f"  Status: Offline (start Ollama)")

        finally:
            session.close()

    def do_monitor(self, path):
        """Monitor a directory for new files to ingest.
        Usage: monitor <directory>
        Example: monitor ~/Downloads"""

        if not path:
            print("Please provide a directory to monitor")
            return

        watch_dir = Path(path).expanduser()
        if not watch_dir.is_dir():
            print(f"Not a directory: {watch_dir}")
            return

        print(f"\n👁️ Monitoring {watch_dir} for new files...")
        print("Press Ctrl+C to stop monitoring\n")

        self.monitoring_active = True

        def monitor_loop():
            seen_files = set(watch_dir.rglob('*'))

            while self.monitoring_active:
                time.sleep(2)
                current_files = set(watch_dir.rglob('*'))
                new_files = current_files - seen_files

                for file_path in new_files:
                    if file_path.is_file() and not file_path.name.startswith('.'):
                        print(f"\n🆕 New file detected: {file_path.name}")
                        try:
                            result = self.ingestor.ingest_file(str(file_path))
                            print(f"  ✓ Auto-ingested as {result['event_id'][:8]}...")
                        except Exception as e:
                            print(f"  ✗ Error: {e}")

                seen_files = current_files

        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()

        try:
            while self.monitoring_active:
                time.sleep(1)
        except KeyboardInterrupt:
            self.monitoring_active = False
            print("\nMonitoring stopped")

    def do_export(self, args):
        """Export your consciousness data.
        Usage: export <format> [output_path]
        Formats: json, csv, markdown
        Example: export json ~/backup.json"""

        if not args:
            print("Usage: export <format> [output_path]")
            return

        parts = args.split()
        format = parts[0]
        output_path = parts[1] if len(parts) > 1 else f"consciousness_export.{format}"

        print(f"\n📤 Exporting to {output_path}...")

        db_manager = get_db_manager()
        session = db_manager.get_session()

        try:
            from consciousness.database import Event
            events = session.query(Event).all()

            if format == 'json':
                data = []
                for event in events:
                    data.append({
                        'id': event.id,
                        'timestamp': event.timestamp.isoformat(),
                        'type': event.event_type,
                        'source': event.source,
                        'metadata': event.meta_data
                    })

                with open(output_path, 'w') as f:
                    json.dump(data, f, indent=2)

            elif format == 'markdown':
                with open(output_path, 'w') as f:
                    f.write("# Consciousness Export\n\n")
                    for event in events:
                        f.write(f"## {event.timestamp}\n")
                        f.write(f"**Type**: {event.event_type}\n")
                        f.write(f"**Source**: {event.source}\n\n")

            else:
                print(f"Unsupported format: {format}")
                return

            print(f"✓ Exported {len(events)} events to {output_path}")

        finally:
            session.close()

    def do_clear(self, args):
        """Clear the screen."""
        os.system('clear' if os.name == 'posix' else 'cls')

    def do_exit(self, args):
        """Exit the terminal."""
        print("\n👋 Goodbye! Your consciousness data is preserved.")
        # Save history
        history_file = Path.home() / '.christ_history'
        readline.write_history_file(history_file)
        return True

    def do_quit(self, args):
        """Exit the terminal."""
        return self.do_exit(args)

    def do_EOF(self, args):
        """Handle Ctrl+D."""
        return self.do_exit(args)

    def default(self, line):
        """Handle unknown commands or chat mode."""
        if self.current_mode == 'chat':
            self._process_chat_message(line)
        else:
            print(f"Unknown command: {line}")
            print("Type 'help' for available commands")

    def do_help(self, args):
        """Show help for commands."""
        if not args:
            print("""
🧠 C.H.R.I.S.T. Terminal Commands
================================

Consciousness Exploration:
  search <query>      - Search your consciousness data
  query <question>    - AI-enhanced question answering (RAG)
  chat [message]      - Chat with your consciousness

Data Management:
  ingest <path>       - Ingest files or directories
  monitor <dir>       - Auto-ingest new files in directory
  export <format>     - Export your data (json/markdown)
  stats              - Show system statistics

System:
  clear              - Clear screen
  help [command]     - Show help
  exit/quit          - Exit terminal

Chat Mode Commands:
  /exit              - Exit chat mode
  /clear             - Clear conversation history
  /history           - Show conversation history

Examples:
  search childhood memories
  query What are my thoughts on consciousness?
  chat Tell me about my philosophical views
  ingest ~/Documents/journal
  monitor ~/Downloads
""")
        else:
            super().do_help(args)

    def cmdloop(self, intro=None):
        """Override to handle different modes."""
        while True:
            try:
                if self.current_mode == 'command':
                    super().cmdloop(intro=intro)
                    break
                else:
                    # Chat mode - simplified loop
                    line = input(self.prompt)
                    self.default(line)
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit")
            except EOFError:
                self.do_exit('')
                break


def main():
    """Launch the C.H.R.I.S.T. interactive terminal."""
    terminal = ChristTerminal()
    terminal.cmdloop()


if __name__ == '__main__':
    main()