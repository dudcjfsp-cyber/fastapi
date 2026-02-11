import os
import asyncio
import sys
import google.generativeai as genai
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from google.generativeai.types import content_types
from collections.abc import Iterable

# API Key Check
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    print("Error: GOOGLE_API_KEY environment variable is not set.")
    print("Please set it using: $env:GOOGLE_API_KEY='your_key'")
    sys.exit(1)

genai.configure(api_key=GOOGLE_API_KEY)

async def main():
    # 1. Start MCP Server
    server_params = StdioServerParameters(
        command="python",
        args=["server_mcp.py"],
        env=os.environ.copy()
    )

    print("🔌 Connecting to MCP Server...", end="", flush=True)
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print(" Connected!")

            # 2. Fetch Tools from MCP
            tools_response = await session.list_tools()
            mcp_tools = tools_response.tools
            print(f"🛠️  Loaded {len(mcp_tools)} tools: {[t.name for t in mcp_tools]}")

            # 3. Define Tools for Gemini
            # We wrap MCP tools directly into a callable dictionary for Gemini
            async def call_mcp_tool(function_call):
                name = function_call.name
                args = function_call.args
                print(f"  🤖 AI calling tool: {name}({args})")
                return await session.call_tool(name, arguments=args)

            def transform_schema(schema):
                """Transform MCP JSON schema to Gemini-compatible schema."""
                if isinstance(schema, dict):
                    new_schema = {}
                    for k, v in schema.items():
                        if k == 'title':
                            continue
                        elif k == 'type' and isinstance(v, str):
                            # Map JSON schema types to Gemini types (uppercase)
                            new_schema[k] = v.upper()
                        else:
                            new_schema[k] = transform_schema(v)
                    return new_schema
                elif isinstance(schema, list):
                    return [transform_schema(i) for i in schema]
                return schema

            gemini_tools_decl = []
            for t in mcp_tools:
                gemini_tools_decl.append({
                    "name": t.name,
                    "description": t.description,
                    "parameters": transform_schema(t.inputSchema)
                })

            # Model Selection Logic
            def get_best_model():
                preferred_models = [
                    'gemini-2.5-flash',
                    'gemini-2.0-flash',
                    'gemini-1.5-flash',
                    'gemini-1.5-pro',
                    'gemini-flash-latest'
                ]
                print("🔍 Searching for available models...")
                available = []
                try:
                    for m in genai.list_models():
                        if 'generateContent' in m.supported_generation_methods:
                            model_name = m.name.replace('models/', '')
                            available.append(model_name)
                    
                    # Check preferences
                    for pref in preferred_models:
                        if pref in available:
                            print(f"✨ Selected Model: {pref}")
                            return pref
                    
                    # Fallback
                    if available:
                        print(f"⚠️ Preferred models not found. Selecting: {available[0]}")
                        return available[0]
                except Exception as e:
                    print(f"⚠️ Model search failed: {e}")
                
                print("⚠️ Defaulting to 'gemini-2.0-flash'")
                return 'gemini-2.0-flash'

            selected_model = get_best_model()

            model = genai.GenerativeModel(
                model_name=selected_model,
                tools=gemini_tools_decl
            )
            chat = model.start_chat(enable_automatic_function_calling=False)

            print("\n🤖 Gemini Fashion Agent Ready! (Type 'quit' to exit)")
            print("-----------------------------------------------------")

            while True:
                try:
                    user_input = input("\nUser: ")
                    if user_input.lower() in ['quit', 'exit']:
                        break
                    
                    response = chat.send_message(user_input)
                    
                    # Tool Use Loop
                    while response.parts[0].function_call:
                        fc = response.parts[0].function_call
                        tool_name = fc.name
                        tool_args = dict(fc.args)
                        
                        # Execute Tool
                        try:
                            result = await session.call_tool(tool_name, arguments=tool_args)
                            tool_output = result.content[0].text
                        except Exception as e:
                            tool_output = f"Error: {str(e)}"
                            
                        print(f"  > Tool Result: {tool_output[:100]}...")

                        # Send result back to Gemini
                        response = chat.send_message(
                            genai.protos.Content(
                                parts=[genai.protos.Part(
                                    function_response=genai.protos.FunctionResponse(
                                        name=tool_name,
                                        response={'result': tool_output}
                                    )
                                )]
                            )
                        )
                    
                    print(f"Agent: {response.text}")

                except Exception as e:
                    print(f"\nError: {e}")

if __name__ == "__main__":
    # Windows event loop policy fix
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
