# 🧠 AI Resume Analyzer

## Overview  
A smart, user-friendly desktop application that analyzes resumes to determine how well they match specific job roles such as **Data Scientist**, **Software Engineer**, **Data Analyst**, and **Product Manager**.  
It evaluates skills, experience, and generates beautiful visual reports to help users improve their resumes.

---

## Algorithm Used  
**Keyword-based Greedy Scoring Algorithm**

- Each job role has a set of weighted keywords (skills & experience terms).  
- The app scans your resume and assigns scores based on keyword matches.  
- Final scores are shown for each role with percentage-based match results and visual graphs.

---

## Steps  
1. Upload or paste your resume (`.pdf`, `.docx`, or `.txt`).  
2. Choose **Analyze Resume** to generate results.  
3. View:
   - Skill Match %
   - Experience Match %
   - Overall Role Fit %
4. Explore interactive visualizations:
   - Match Comparison Chart  
   - Skill Frequency Treemap  
   - Radar Chart  
5. Manage job roles easily from the **⚙ Manage Roles** tab (edit, add, delete roles).  

---
Key Features
📄 Multi-Format Upload: Load resumes from .pdf, .docx, or .txt files, or simply paste the text directly.

🖼️ PDF Preview: See an instant preview of the first page of any uploaded PDF.

📊 Dynamic Analysis: Get immediate feedback on how a resume matches different job roles.

💯 Detailed Scoring: View separate percentage scores for Skill Match and Experience Match, combined into an Overall Score.

❗ Skill Gap Analysis: Instantly see which key skills are found in the resume and which are missing for your target job.

💡 Smart Recommendations: Get a "Top Recommendation" highlighting the best-matched role and the most valuable missing keywords.

---

📈 Rich Data Visualizations:

Match Comparison: A bar chart comparing match scores across all roles.

Skill Treemap: A visual breakdown of all skills found and their frequency.

Top Skills Chart: A horizontal bar chart of the most frequent skills.

Role-Fit Radar Chart: A spider-web chart showing overall fit across all defined roles.

---

⚙️ Fully Customizable Roles:

A dedicated "Manage Roles" tab lets you add, edit, and delete job roles live.

Easily update the keywords and their weights for both skills and experience.

All changes are automatically saved to job_roles.json.

🎨 Theme Toggle: Switch between a sleek dark mode and a clean light mode with a single click.

---

🛠️ Technology Stack
GUI: Python, tkinter, ttkbootstrap (for modern themes and widgets)

File Reading: PyMuPDF (fitz), python-docx

Data Analysis: pandas, numpy

Data Visualization: matplotlib, seaborn, squarify

Image Handling: Pillow (PIL) (for PDF preview)

---

## How to Run  
1. Unzip the folder.  
2. Make sure you have Python 3 installed.  
3. Install dependencies:  
   ```bash
   pip install ttkbootstrap pandas numpy matplotlib seaborn PyMuPDF python-docx pillow squarify
