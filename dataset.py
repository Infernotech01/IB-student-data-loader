import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

class LoadDataset():

    def load_data(filename):
        """Used to load data from given filepath
        """

        excel = pd.ExcelFile(filename)
        sheets = ['MYP STUDENT MASTER', 'MYP SUBJECT MASTER', 'MYP STUDENT GRADES']
        student, subject, grades = [excel.parse(sheet) for sheet in sheets]
        return (student, subject, grades)

    def preprocess_data(data_dfs):
        student, subject, grades = data_dfs
        student_dct = {}
        subject_dct = {}

        myp_keys = list(student.keys()[-6:-1])
        for key in myp_keys:
            df = subject[subject['MYP'] == key]

            subject_dct[key] = {}
            subject_dct[key]['Subjects'] = {}
            subject_dct[key]['Students'] = []
            sub_dct = subject_dct[key]['Subjects']

            for index, row in df.iterrows():
                myp_data = {
                    'Subject_Name' : row['SUBJECT NAME'],
                    'Achievements' : row.tolist()[-4:]
                }
                sub_dct[row['SUBJECT ID']] = myp_data

        for index, row in student.iterrows():
            student_id = row['Student ID']
            myp_list = [key for key in myp_keys if row[key] == 'YES']

            for key in myp_list:
                data = subject_dct[key]['Students']
                data.append(student_id)
                subject_dct[key]['Students'] = data

            student_data = {
                'First_Name' : row['First Name'].strip(), 
                'Last_Name' : row['Last Name'].strip(),
                'Year_Of_Joining' : int(row['Year Of Joining']),
                'MYP_List' : myp_list,
                'MYP_Completion' : int(row['YEAR OF MYP COMPLETION'])
            }

            marks = {}
            grades_student = grades[grades['STUDENT ID'] == student_id]
            
            for term_name, term_group in grades_student.groupby(by='TERM'):
                term_name = 'TERM'+str(int(term_name))
                marks[term_name] = {}
                
                for index, row in term_group.iterrows():
                    subject_id = row['SUBJECT ID']
                    subject_data = row.tolist()[-5:-1]
                    data = marks.get(subject_id, subject_data)
                    marks[term_name][subject_id] = data

            student_data['Marks'] = marks
            data = student_dct.get(student_id, student_data)
            student_dct[student_id] = data
            
        return (student_dct, subject_dct)

    def generate_plot(student, subject, student_id, student_term, student_myp):
        columns = ['Subjects', 'Achievement Names', 'Achievements', 'Marks']
        subjects = list(subject[student_myp]['Subjects'].keys())
        df = pd.DataFrame(columns = columns)

        for subject_name in subjects:
            marks = student[student_id]['Marks'][student_term][subject_name]
            Achievement_names = subject[student_myp]['Subjects'][subject_name]['Achievements']
            achievements = ['A', 'B', 'C', 'D']
            zipped = zip(marks, Achievement_names, achievements)
            
            for mark, name, achievement in zipped:
                df = df.append({
                    'Subjects' : subject_name,
                    'Achievement Names' : name,
                    'Achievements' : achievement.strip(),
                    'Marks' : mark
                }, ignore_index=True)

        subjects_avg = []
        student_ids = subject[student_myp]['Students']
        for subject_id in subjects:
            subject_avg = []
            
            for student_id in student_ids:
                marks = student[student_id]['Marks'][student_term][subject_id]
                subject_avg.append(np.sum(marks))
            
            subjects_avg.append(np.average(subject_avg))

        fig = px.bar(df, x="Subjects", y="Marks", 
             hover_name="Achievement Names", 
             color="Achievements")

        fig.add_trace(go.Scatter(
            x=df['Subjects'].unique(),
            y=subjects_avg,
            name='class average'
        ))

        return fig;

