import pdfplumber
import pandas as pd


def extract_subjects(path):
    with pdfplumber.open() as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
            tables = page.extract_tables()  # Extract tables as a list of lists


        cleaned_tables = []
        for table in tables:
            df = pd.DataFrame(table)
            df.columns = df.iloc[0]  # Set the first row as column headers
            df = df[1:]  # Remove the header row
            cleaned_tables.append(df)


        df = pd.DataFrame(cleaned_tables[0])

        ## list columns of df
        # list(cleaned_tables[0].columns.values)
        df.columns = ['Course\nCode', 'Course Title', 'Grade', 'Credit', 
                    'Course\nCode.1', 'Course Title.1', 'Grade.1', 'Credit.1']

        merged_df = pd.DataFrame({
            'Course\nCode': df['Course\nCode'].tolist() + df['Course\nCode.1'].tolist(),
            'Course Title': df['Course Title'].tolist() + df['Course Title.1'].tolist(),
            'Grade': df['Grade'].tolist() + df['Grade.1'].tolist(),
            'Credit': df['Credit'].tolist() + df['Credit.1'].tolist()
        })

        merged_df.dropna()






path = "transcript_sample/6310400908.pdf"
data = extract_subjects(path)
print(data)