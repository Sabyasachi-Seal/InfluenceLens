import os

import pandas as pd
from llama_index.core import VectorStoreIndex, Document, StorageContext, load_index_from_storage

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import uuid
from typing import Dict, List
from consts.consts import ModelConfig

class ContentReviewApp:
    def __init__(self, csv_path: str, storage_path: str = "./storage"):
        self.csv_path = csv_path
        self.storage_path = storage_path
        self.df = self.load_and_clean_data()
        self.llm = ChatGoogleGenerativeAI(model=ModelConfig.LLM_MODEL, temperature=0.2)
        self.brief_index = self.load_or_create_brief_index()
        self.feedback_prompt = self.create_feedback_prompt()
        self.brief_ids = []

    def get_campaign_ids(self) -> List[str]:
        """Return a list of unique campaign IDs"""
        return self.df['campaignId'].unique().tolist()

    def load_and_clean_data(self) -> pd.DataFrame:
        """Load and clean the Milanote activities CSV"""
        df = pd.read_csv(self.csv_path)
        
        df = df.dropna(subset=['campaignId', 'message'])
        df['message'] = df['message'].str.strip()
        
        self.briefs = df[df['message'].str.contains("Submitted Brief", case=False)]
        self.submissions = df[df['deliverableInput'].notna()]

        return df

    def load_or_create_brief_index(self) -> VectorStoreIndex:
        """Load existing index from disk or create a new one"""
        if os.path.exists(self.storage_path):

            storage_context = StorageContext.from_defaults(persist_dir=self.storage_path)
            return load_index_from_storage(storage_context)
        else:
            documents = []
            for _, row in self.briefs.iterrows():
                doc = Document(
                    text=row['message'],
                    metadata={
                        "campaignId": row['campaignId'],
                        "type": row['type']
                    },
                    doc_id=str(uuid.uuid4())
                )
                documents.append(doc)
            
            index = VectorStoreIndex.from_documents(documents)
            index.storage_context.persist(persist_dir=self.storage_path)
            return index

    def create_feedback_prompt(self) -> LLMChain:
        template = """
        You are an expert content reviewer for influencer marketing campaigns.
        Given a brand brief and an influencer's submission, provide detailed feedback.

        Brand Brief:
        {brief}

        Influencer Submission:
        {submission}

        Instructions:
        1. Identify which key points from the brief are well-addressed in the submission
        2. Highlight any missing elements or areas needing improvement
        3. Provide specific suggestions for improvement
        4. Maintain a professional and constructive tone

        Feedback Format:
        ### Feedback
        #### Strengths
        - [List strengths]

        #### Areas for Improvement
        - [List areas needing improvement]

        #### Suggestions
        - [List specific suggestions]
        """
        prompt = PromptTemplate(
            input_variables=["brief", "submission"],
            template=template
        )
        return LLMChain(llm=self.llm, prompt=prompt)

    def get_relevant_brief(self, campaign_id: str) -> str:
        query = f"campaignId:{campaign_id}"
        retriever = self.brief_index.as_retriever(similarity_top_k=1)
        nodes = retriever.retrieve(query)
        return nodes[0].text if nodes else ""

    def review_submission(self, campaign_id: str, submission: str) -> Dict[str, str]:
        brief = self.get_relevant_brief(campaign_id)
        if not brief:
            return {"error": "No brief found for campaign"}

        feedback = self.feedback_prompt.run(brief=brief, submission=submission)
        return {
            "campaign_id": campaign_id,
            "feedback": feedback,
            "brief": brief,
            "submission": submission
        }

    def generate_random_submission(self) -> str:
        prompt = PromptTemplate(
            input_variables=[],
            template="""
            Generate a realistic influencer submission for a fictional marketing campaign. 
            The submission can be a video topic, draft script, or content description. 
            It should include:
            - A description of the content (e.g., video idea, script outline)
            - Mention of a product or service
            - A call-to-action
            The submission should be concise and mimic what an influencer might submit for brand review.
            """
        )
        chain = LLMChain(llm=self.llm, prompt=prompt)
        return chain.run({})

    def generate_random_brief(self) -> str:
        prompt = PromptTemplate(
            input_variables=[],
            template="""
            Generate a realistic brand brief for an influencer marketing campaign for a fictional product or service. 
            The brief should include:
            - A clear description of the product/service
            - Key selling points to highlight
            - Target audience
            - Tone and style guidelines
            - Specific requirements for the content (e.g., video length, hashtags, or call-to-action)
            The brief should be concise, professional, and suitable for an influencer to create content from.
            """
        )
        chain = LLMChain(llm=self.llm, prompt=prompt)
        return chain.run({})
