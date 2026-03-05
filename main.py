import os
import sys
import asyncio
import argparse
from core.orchestrator import Orchestrator


async def main():
    # Force UTF-8 encoding for standard output to avoid UnicodeEncodeError on Windows
    # when printing characters like non-breaking hyphens (\u2011) that cp1254/cp1252 doesn't support.
    if sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="VibeArchitect Orchestrator CLI")
    parser.add_argument(
        "--path", type=str, required=True, help="Project directory path"
    )
    parser.add_argument(
        "--vibe", type=str, required=True, help="The high-level idea/vibe"
    )
    args = parser.parse_args()

    print(f"--- VibeArchitect Starting ---")
    print(f"Project Path: {args.path}")
    print(f"Vibe: {args.vibe}")
    print(f"------------------------------\n")

    orchestrator = Orchestrator(args.path)

    async for message in orchestrator.run_pipeline(args.vibe):
        if message.raw_stream:
            # Print raw stream without newline for the 'typing' effect
            print(message.raw_stream, end="", flush=True)
        else:
            # Print status updates on new lines
            print(f"\n[{message.agent}] {message.status}: {message.thought_process}")
            if message.data_update:
                print(f"Data Received: {len(str(message.data_update))} bytes")

    print(f"\n--- Blueprint Generation Completed ---")


if __name__ == "__main__":
    asyncio.run(main())
