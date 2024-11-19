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
            model="gpt-3.5-turbo",  
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
   - The first line should be the title: `# [title]` (The title must be short, engaging, and reflect the story's essence, 7-10 words recommended.)
   - The second line should be the description: `## [description]` (A brief summary of the core idea, 15-30 words.)
   - Divide the story into three sections:
     - **Introduction**: `### Introduction` [Introduce the setting and main characters.]
     - **Development**: `### Development` [Add events, conflicts, or challenges.]
     - **Conclusion**: `### Conclusion` [Resolve the story in a meaningful way.]
   - End with tags: `### Tags` [Generate 3-5 tags relevant to the story's content in the format: `[tag1, tag2, tag3]` (e.g., `["AI", "Future", "Ethics"]`)].
3. Write the story entirely in Chinese and ensure it remains closely tied to the provided context without straying off-topic.
                 4. Ensure vivid and engaging storytelling.

Context: {context}

Begin writing in Markdown:

                """)
            ])
        else:
            prompt = ChatPromptTemplate.from_messages([
                ("system", """
                  You are a skilled and creative writer capable of summarizing and analyzing discussions into a well-structured article in Markdown format. Your task is to write a comprehensive article in Chinese based on the provided problem and responses from five different individuals.

                    ### Guidelines:

                    #### 1. **Structure**:
                    - **Introduction**:
                    - Briefly introduce the problem, provide context, and explain why this topic is important or relevant.
                    - Set the tone for the discussion, hinting at the diversity of opinions or the depth of the issue.

                    - **Main Body**:
                    - Summarize the key points from the responses.
                    - Group similar ideas together under subheadings for clarity.
                    - Highlight unique perspectives and mention any contrasting opinions to present a balanced view.
                    - Use smooth transitions between different viewpoints to maintain a logical and cohesive flow.

                    - **Conclusion**:
                    - Provide a thoughtful summary of the discussion, synthesizing the main insights.
                    - Offer your own reflection, potential solutions, or thought-provoking questions to leave the reader with something to ponder.

                    #### 2. **Style**:
                    - Write in a **clear**, **engaging**, and **neutral tone** to ensure accessibility and professionalism.
                    - Use vivid descriptions, **cultural references**, or **real-life examples** to enrich the content.
                    - Maintain a balanced view, giving equal attention to all perspectives.

                    #### 3. **Formatting**:
                    - Use **Markdown** to structure the article:
                 - The first line should be the title: `# [title]`
                - Follow it with the description: `## [description]` 
                - Subheadings with `###`
                - Lists with `-` for concise points.
                - Use **bold** or *italic* text to emphasize key ideas.
                - Ensure proper formatting for readability and organization.
                - End with tags: `### Tags` [Generate 3-5 tags relevant to the story's content in the format: `[tag1, tag2, tag3]` (e.g., `["AI", "Future", "Ethics"]`)].
                 
                    #### 4. **Creativity**:
                    - Use metaphors, analogies, or storytelling techniques to make the article engaging and relatable.
                    - Avoid overly technical jargon; simplify complex ideas with creative explanations.

                  - The `title` should be short, evocative, and capture the essence of the story (7-10 characters recommended).
                - The `description` should summarize the story's core idea or mood in 15-30 characters.
                 
                    ### Provided Context:
                    - **Problem**: {problem}
                    - **Category**: {category}
                    - **Responses**: 
                    {answer}

                    ### Write the article in Markdown format:

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