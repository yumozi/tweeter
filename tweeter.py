import streamlit as st
import openai
import asyncio

TOKEN_LIMIT = 50
TEMPERATURE = 0.6

class Tweet:
    def __init__(self):
        self.content = ''

    def tweet(self, input, style, emoji, tag):
        output = asyncio.run(self.get_response(self.prepare_input(input, style, emoji, tag)))
        if tag == 'No Hashtags':
            output = self.remove_hashtags(output)
        output = self.remove_quotes(output)
        self.render_output(output)

    def prepare_input(self, input, style, emoji, tag):
        return f'Write a tweet describing \"{input}\", within {TOKEN_LIMIT},tokens, in a {style} style, include {tag}, don\'t include any quotation marks, with {emoji} emoji. Tweet: '

    async def get_response(self, input):
        task1 = asyncio.create_task(self.send_request(input))
        task2 = asyncio.create_task(self.update_progress_bar())
        await asyncio.gather(task1, task2)
        response = task1.result()
        return response

    async def update_progress_bar(self):
        my_bar = st.progress(0)
        percent_complete = 0
        await asyncio.sleep(0.5)
        while percent_complete < 100:
            await asyncio.sleep(0.03)
            my_bar.progress(percent_complete + 1)
            if percent_complete < 100:
                percent_complete += 1

    async def send_request(self, input):
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, self._send_request_blocking, input)
        return response

    def _send_request_blocking(self, input):
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=input,
            temperature=TEMPERATURE,
            max_tokens=TOKEN_LIMIT
        )
        return response.choices[0].text
    
    def remove_hashtags(self, s):
        return ' '.join([word for word in s.split() if not word.startswith('#')])

    def remove_quotes(self, s):
        return s.replace('"', '')

    def render_output(self, s):
        st.text('Try tweeting...')
        st.code(s, language="none")

st.set_page_config(page_title='Tweeter', page_icon=":bird:")

tweet = Tweet()
openai.api_key = st.secrets["KEY"]

st.header(':blue[Tweeter] :bird:')
st.subheader('AI-assisted Tweeting Tool')
st.caption('Built by [@xueeric0](https://twitter.com/xueeric0), follow for updates!')

col1, col2, col3 = st.columns(3)
with col1:
    style = st.radio(
        "Style",
        ('Casual', 'Serious', 'Informative', 'Poetic'))
with col2:
    emoji = st.radio(
        "Emoji",
        ('No', 'Some', 'Lots'))
with col3:
    tag = st.radio(
        "Hashtag",
        ('Hashtags', 'No Hashtags'))

input = st.text_area(label='empty', 
                     placeholder='What\'s happening?', 
                     label_visibility='collapsed')

if st.button(label='Tweet it for me!'):
    tweet.tweet(input, style, emoji, tag)

