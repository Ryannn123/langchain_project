from pprint import pprint

from dotenv import load_dotenv
from langchain.messages import HumanMessage, AIMessage, AnyMessage
from langchain_core.runnables import RunnableConfig

from src.graph import build_graph
from src.utils import calculate_token_cost

load_dotenv()

def print_output(output, token_usage):
    print('\nExtracted info:')
    pprint(output['student_profile'].model_dump(), indent=2)
    print('\nToken Usage')
    print(f'Total input tokens: {token_usage['input_tokens']}')
    print(f'Total output tokens: {token_usage['output_tokens']}')
    print(f'Total costs: RM {calculate_token_cost(token_usage)}')
    # print(f'Total llm call: {llm_call['count']}')
    print()

def print_result(stream, token_usage, llm_call):
    for message in stream.messages:
        llm_call['count'] += 1
        if message.node == 'extraction':
            for token in message.reasoning:
                print('\n[Thinking]')
                print({token}, end='', flush=True)
        else:
            print('\n(AI):')
            for token in message.text:
                print(token, end='', flush=True)
            print()
            
        if message.output and message.output.usage_metadata:
            usage = message.output.usage_metadata
            token_usage['input_tokens'] = usage['input_tokens'] + token_usage['input_tokens']
            token_usage['output_tokens'] = usage['output_tokens'] + token_usage['output_tokens']

graph = build_graph()
config: RunnableConfig = {'configurable': {'thread_id': 'thread-1'}}

first_msg = AIMessage('May I know what course you plan to study?')

token_usage = {'input_tokens': 0, 'output_tokens': 0}
llm_call = {'count': 0}

stop_chat = False
sent_first_msg = False

while not stop_chat:
    if not sent_first_msg:
        print(f'(AI): {first_msg.content}')
        print()
    
    print()
    human = HumanMessage(input('(Student): '))
    messages: list[AnyMessage] = []
    if not sent_first_msg:
        messages = [first_msg, human]
    else:
        messages = [human]
    
    sent_first_msg = True
    
    stream = graph.stream_events({'messages': messages, 'course_state': {'max_indecision_count': 3}}, config=config, version='v3')
    print_result(stream, token_usage, llm_call)
    
    output = stream.output
    # print_output(output, token_usage)
    stop_chat = output.get('completed', False)
    
final_state = graph.get_state(config)
print_output(final_state.values, token_usage)