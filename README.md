# AI-Powered Psychometric & Stream Selection Platform

An open-source, copyright-safe student psychometric testing platform supporting live interactive testing, batch paper-test evaluation via Excel, and automated AI counseling reports powered by **Google Gemini** or **ChatGPT**.

---

## Key Features

1. **Dual Evaluation Channels:** Direct web assessment for students or batch `.xlsx` upload for paper-based testing.
2. **Item-ID Framework:** Dynamically scores test sheets with varied question ordering using normalized Item IDs.
3. **AI Counselor Integration:** Uses Google GenAI (`gemini-2.5-flash`) or OpenAI (`gpt-4o-mini`) to write personalized guidance summaries.
4. **Automated PDF Generator:** Produces one-click downloadable PDF reports via ReportLab.
5. **Legally Safe & Commercial-Ready:** Built using public-domain scales (IPIP & Holland RIASEC).

---

## Setup & Execution

### 1. Configure Environment Variables
Create a `.env` file in the root folder:
```env
GEMINI_API_KEY="your-gemini-api-key"
OPENAI_API_KEY="your-openai-api-key"
