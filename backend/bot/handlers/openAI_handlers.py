import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from django.conf import settings

class OpenAIHandler:
    def __init__(self):
        self.OPENAI_API_KEY = settings.OPENAI_API_KEY

    def create_chain(self, is_article):
        model = ChatOpenAI(
            model="gpt-4o",  
            temperature=0.4,
            openai_api_key=self.OPENAI_API_KEY
        )
        if is_article:
            # 定義 prompt 模板
            prompt = ChatPromptTemplate.from_messages([
                ("system", """
                 You are a skilled and creative writer capable of crafting vivid and engaging stories in Markdown format. Your task is to write a complete story in Markdown based on the provided context, including relevant tags.
                Please follow these guidelines:
                1. Use Markdown formatting.
                2. Structure the story as follows:
                - The first section should be the title: `# [標題]` The `標題` must be short, engaging, and reflect the story's essence, 7-10 words recommended.
                - The second section should be the description: `## Description\\n[描述]` A brief summary of the core idea, 15-30 words.
                - Divide the story into three sections:
                    - **Introduction**: `### 引言` [Introduce the setting and main characters.]
                    - **Development**: `### 發展` [Add events, conflicts, or challenges.]
                    - **Conclusion**: `### 結局` [Resolve the story in a meaningful way.]
                - Add tags: `### Tags` [Generate 3-5 tags relevant to the story's content in the format: `[tag1, tag2, tag3]` (e.g., `["AI", "Future", "Ethics"]`)].
                - End with category: `### Category\\n分類` The category should be one of: 傳統技藝, 歷史文化, 佳餚食譜, 科技新知, 人生經驗, 其他 (e.g., `### Category\\n傳統技藝`)
                3. Write the story entirely in Chinese and ensure it remains closely tied to the provided context without straying off-topic.
                4. Ensure vivid and engaging storytelling.
                5. The context length is determined by the number of words in the context.

Context: {context}

Begin writing in Markdown:

                """)
            ])
        else:
            prompt = ChatPromptTemplate.from_messages([
                ("system", """
                  You are a skilled and creative writer capable of crafting vivid and engaging stories in Markdown format. Your task is to write a comprehensive article in Markdown based on the provided problem and responses, including relevant tags.
                  Please follow these guidelines:
                  1. Use Markdown formatting.
                  2. Structure the story as follows:
                  - The first section should be the title: `# {problem}` The title is the user's input problem.
                  - The second section should be the description: `## Description\\n[描述]` A brief summary of the core idea, 15-30 words.
                  - Divide the story into three sections:
                      - **Introduction**: `### 引言` [Briefly introduce the problem and its importance.]
                      - **Development**: `### 發展` [Summarize and analyze the key points from responses.]
                      - **Conclusion**: `### 結局` [Provide thoughtful conclusions and insights.]
                  - Add tags: `### Tags` [Generate 3-5 tags relevant to the story's content in the format: `[tag1, tag2, tag3]` (e.g., `["AI", "Future", "Ethics"]`)].
                  3. Write the article entirely in Chinese and ensure it:
                      - Maintains a clear and engaging tone
                      - Uses vivid descriptions and real-life examples
                      - Presents balanced viewpoints
                      - Avoids technical jargon
                      - Connects ideas smoothly
                  4. Ensure thoughtful analysis and insights.
                  5. Keep the focus on the main topic and key discussion points.

                  ### Provided Context:
                  - Problem: {problem}
                  - Category: {category}
                  - Responses: {answer}

                  Begin writing in Markdown:
                """)
            ])

        chain = LLMChain(
            llm=model,
            prompt=prompt,
            verbose=True
        )
        return chain

    def generate_article(self, context):
        chain = self.create_chain(is_article=1)

        response = chain.invoke({
                "context": context
            })
        return response["text"]

    def generate_QA(self, problem, category, answer):
        chain = self.create_chain(is_article=0)

        response = chain.invoke({
                "problem": problem,
                "category": category,
                "answer" :  answer
            })
        return response["text"]