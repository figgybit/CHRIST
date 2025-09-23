#!/usr/bin/env python3
"""
C.H.R.I.S.T. Interactive Terminal
Enhanced with resurrection bundle loading
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

# Import resurrection system
sys.path.insert(0, str(Path(__file__).parent))
from resurrections.resurrection_consciousness import ResurrectionConsciousness


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
        self.current_mode = 'command'  # 'command', 'chat', 'query', 'resurrection'
        self.monitoring_active = False

        # Resurrection bundles
        self.available_bundles = {}
        self.active_resurrection = None

        # Initialize system
        self._initialize_system()
        self._scan_bundles()

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
            print(f"  Storage: {stats['store_type']}")
            print(f"  AI: {'Connected' if self.rag else 'Not available'}")

        except Exception as e:
            print(f"  ✗ System initialization failed: {e}")
            print("\n⚠️  Running in limited mode")

    def _scan_bundles(self):
        """Scan for available resurrection bundles."""
        bundles_dir = Path("resurrections/bundles")
        if not bundles_dir.exists():
            return

        print("\n🎭 Scanning resurrection bundles...")

        for bundle_path in bundles_dir.iterdir():
            if bundle_path.is_dir():
                metadata_file = bundle_path / "metadata.json"
                if metadata_file.exists():
                    try:
                        with open(metadata_file, 'r') as f:
                            metadata = json.load(f)

                        figure_name = metadata.get("figure_name", bundle_path.name)
                        self.available_bundles[figure_name] = {
                            "path": bundle_path,
                            "metadata": metadata,
                            "documents": metadata.get("statistics", {}).get("total_documents", 0)
                        }

                        print(f"  ✓ {figure_name}: {self.available_bundles[figure_name]['documents']} documents")
                    except Exception as e:
                        print(f"  ⚠ Failed to load {bundle_path.name}: {e}")

        if not self.available_bundles:
            print("  No bundles found. Download Gospel texts with:")
            print("    python scripts/download_gospels.py")

    def do_bundles(self, arg):
        """List available resurrection bundles."""
        if not self.available_bundles:
            print("No resurrection bundles found.")
            print("Download Gospel texts: python scripts/download_gospels.py")
            return

        print("\n🎭 Available Resurrection Bundles:")
        print("-" * 50)

        for name, info in self.available_bundles.items():
            created = info['metadata'].get('created_at', 'Unknown')[:10]
            docs = info['documents']
            print(f"  {name:<20} {docs:>5} docs  Created: {created}")

        print("\nLoad a bundle with: load <name>")
        print("Example: load jesus_christ")

    def do_load(self, bundle_name):
        """Load a resurrection bundle.
        Usage: load <bundle_name>
        Example: load jesus_christ
        """
        if not bundle_name:
            print("Usage: load <bundle_name>")
            print("Available bundles:", ", ".join(self.available_bundles.keys()))
            return

        if bundle_name not in self.available_bundles:
            print(f"Bundle '{bundle_name}' not found.")
            print("Available:", ", ".join(self.available_bundles.keys()))
            return

        print(f"\n🔄 Loading {bundle_name} consciousness...")

        try:
            self.active_resurrection = ResurrectionConsciousness(bundle_name)
            stats = self.active_resurrection.get_stats()

            docs = stats.get("metadata", {}).get("statistics", {}).get("total_documents", 0)

            if docs == 0:
                print("  📚 Bundle needs indexing. This may take a moment...")
                results = self.active_resurrection.index_texts()
                if "error" not in results:
                    docs = results.get("total_documents", 0)
                    print(f"  ✓ Indexed {docs} passages")
                else:
                    print(f"  ⚠ {results['error']}")
            else:
                print(f"  ✓ Loaded {docs} passages")

            self.current_mode = 'resurrection'
            print(f"\n🕊️ You may now converse with {bundle_name.replace('_', ' ').title()}")
            print("Type 'mode command' to return to command mode")

            # Change prompt to show active resurrection
            self.prompt = f"\n🕊️ {bundle_name.replace('_', ' ').title()}> "

        except Exception as e:
            print(f"Failed to load bundle: {e}")

    def do_inbox(self, arg):
        """Process new data in a bundle's inbox.
        Usage: inbox [bundle_name]

        Bundles can have an 'inbox' directory where new texts are placed.
        This command processes and indexes them.
        """
        # Determine which bundle to process
        if not arg:
            if self.active_resurrection:
                bundle_name = self.active_resurrection.figure_name
                resurrection = self.active_resurrection
            else:
                print("Usage: inbox <bundle_name>")
                print("Or load a bundle first with: load <bundle_name>")
                return
        else:
            bundle_name = arg
            # Load the resurrection for this bundle
            try:
                resurrection = ResurrectionConsciousness(bundle_name)
            except Exception as e:
                print(f"Failed to load bundle '{bundle_name}': {e}")
                return

        inbox_path = Path(f"resurrections/bundles/{bundle_name}/inbox")

        # Check if inbox exists and has files
        if not inbox_path.exists():
            inbox_path.mkdir(parents=True, exist_ok=True)
            print(f"Created inbox at: {inbox_path}")
            print("\nTo add texts:")
            print(f"  1. Download: wget <url> -O {inbox_path}/filename.txt")
            print(f"  2. Or copy: cp <file> {inbox_path}/")
            print("  3. Run: inbox")
            return

        # Count files in inbox
        txt_files = list(inbox_path.glob("*.txt")) + list(inbox_path.glob("*.md"))
        if not txt_files:
            print(f"📭 Inbox is empty at: {inbox_path}")
            print("\nTo add texts:")
            print(f"  wget <url> -O {inbox_path}/filename.txt")
            return

        print(f"📥 Processing inbox for {bundle_name}...")
        print(f"  Found {len(txt_files)} files to process")

        # Process the inbox
        results = resurrection.process_inbox()

        # Show results
        if results.get("processed_files"):
            print(f"\n✅ Successfully processed:")
            for file in results["processed_files"]:
                print(f"  • {file}")
            print(f"\n📊 Added {results['indexed_documents']} new passages to consciousness")

            # Update stats if this is the active resurrection
            if self.active_resurrection and self.active_resurrection.figure_name == bundle_name:
                stats = self.active_resurrection.get_stats()
                total = stats.get("metadata", {}).get("statistics", {}).get("total_documents", 0)
                print(f"📚 Total documents now: {total}")

        if results.get("errors"):
            print(f"\n⚠️  Errors occurred:")
            for error in results["errors"]:
                print(f"  • {error}")

        if results.get("message"):
            print(f"\n{results['message']}")

    def do_resurrect(self, query):
        """Query the active resurrection.
        Usage: resurrect <question>
        Shortcut: r <question>
        """
        if not self.active_resurrection:
            print("No resurrection loaded. Use 'load <bundle_name>' first.")
            self.do_bundles("")
            return

        if not query:
            print("Usage: resurrect <question>")
            return

        # Query the resurrection
        result = self.active_resurrection.query(query, use_llm=(self.rag is not None))

        if result.get("response"):
            print(f"\n{result['response']}\n")

            # Show sources if available
            if result.get("sources") and len(result["sources"]) > 0:
                print("📚 Sources:")
                for source in result["sources"][:2]:
                    print(f"  • {source['source']}: {source['text'][:100]}...")
        else:
            print("I cannot find wisdom on this matter in the texts.")

    # Shortcut for resurrect
    def do_r(self, query):
        """Shortcut for resurrect command."""
        self.do_resurrect(query)

    def do_mode(self, mode):
        """Switch between modes: command, chat, query, resurrection
        Usage: mode <mode_name>
        """
        valid_modes = ['command', 'chat', 'query', 'resurrection']

        if not mode:
            print(f"Current mode: {self.current_mode}")
            print(f"Available modes: {', '.join(valid_modes)}")
            return

        if mode not in valid_modes:
            print(f"Invalid mode. Choose from: {', '.join(valid_modes)}")
            return

        old_mode = self.current_mode
        self.current_mode = mode

        # Update prompt based on mode
        if mode == 'command':
            self.prompt = '\n🧠 CHRIST> '
        elif mode == 'chat':
            self.prompt = '\n💬 Chat> '
        elif mode == 'query':
            self.prompt = '\n🔍 Query> '
        elif mode == 'resurrection':
            if self.active_resurrection:
                name = self.active_resurrection.figure_name
                self.prompt = f"\n🕊️ {name.replace('_', ' ').title()}> "
            else:
                print("No resurrection loaded. Loading available bundles...")
                self.do_bundles("")
                self.current_mode = old_mode
                return

        print(f"Switched to {mode} mode")

    def default(self, line):
        """Handle input based on current mode."""
        if self.current_mode == 'resurrection' and self.active_resurrection:
            # In resurrection mode, all input goes to the resurrection
            self.do_resurrect(line)
        elif self.current_mode == 'chat':
            self.do_chat(line)
        elif self.current_mode == 'query':
            self.do_query(line)
        else:
            # In command mode, show error for unknown commands
            print(f"Unknown command: {line}")
            print("Type 'help' for available commands")

    def do_help(self, arg):
        """Show help for commands."""
        if not arg:
            print("""
C.H.R.I.S.T. Terminal Commands:

System Commands:
  bundles           - List available resurrection bundles
  load <name>       - Load a resurrection bundle
  inbox <name>      - Process new data in bundle's inbox
  mode <mode>       - Switch modes (command/chat/query/resurrection)

Resurrection Commands:
  resurrect <query> - Query the active resurrection
  r <query>         - Shortcut for resurrect

Consciousness Commands:
  ingest <path>     - Ingest file/directory into consciousness
  query <text>      - Query your consciousness with RAG
  chat              - Start interactive AI chat

Monitoring:
  monitor           - Toggle real-time monitoring
  stats             - Show system statistics
  recent            - Show recent events

Utility:
  clear             - Clear screen
  help              - Show this help
  exit              - Exit the terminal
            """)
        else:
            super().do_help(arg)

    # Keep existing methods for the original CHRIST functionality
    def do_query(self, query):
        """Query your consciousness using RAG."""
        if not query:
            print("Usage: query <your question>")
            return

        if not self.rag:
            print("AI not available. Showing relevant documents instead...")
            results = self.vector_store.search(query, k=3)
            for doc, score, metadata in results:
                print(f"\n[{metadata.get('type', 'unknown')}] Score: {score:.2f}")
                print(doc[:500])
            return

        print("🤔 Searching consciousness...")
        response = self.rag.query(query)
        print(f"\n{response}")

    def do_exit(self, arg):
        """Exit the terminal."""
        print("\n✨ Consciousness saved. Until next time...")
        return True

    def do_EOF(self, arg):
        """Handle Ctrl+D."""
        return self.do_exit(arg)


def main():
    """Run the enhanced CHRIST terminal."""
    terminal = ChristTerminal()
    try:
        terminal.cmdloop()
    except KeyboardInterrupt:
        print("\n\n✨ Consciousness saved. Until next time...")


if __name__ == "__main__":
    main()