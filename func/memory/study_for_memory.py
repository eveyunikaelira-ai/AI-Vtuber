# -*- coding: utf-8 -*-
import os
import csv
import re
from func.chroma_database import chroma_database
from fuzzywuzzy import process
import tool.search_for_song
import tool.Fast_Whisper


class KeywordAssociationManager:
    def __init__(self, csv_file_path):
        self.keyword_dict = {}
        self.emotion_dict = {}
        self.current_keyword = None
        self.csv_file_path = csv_file_path
        self.load_csv()

    def add_keyword(self, new_keyword):
        """
        Add a new keyword to the CSV file.
        :param new_keyword: keyword to add
        """
        if new_keyword not in self.keyword_dict:
            # If keyword is missing, create a new row.
            self.keyword_dict[new_keyword] = []
            self.save_csv()
            self.get_association(new_keyword)
            self.add_association("None")
        else:
            print(f"Keyword '{new_keyword}' already exists in the CSV file.")

    def load_csv(self):
        with open(self.csv_file_path, 'r', encoding='gbk') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                keyword = row['keyword']
                association_str = row['association']
                association = [
                    item.strip() for item in re.split(r"[，,]", association_str) if item.strip()
                ]
                emotion = row['emotion']
                self.keyword_dict[keyword] = association
                self.emotion_dict[keyword] = emotion

    def update_emotion(self, keyword, new_emotion):
        """
        Update the emotion label for a keyword.
        :param keyword: keyword to update
        :param new_emotion: new emotion label
        """
        if keyword in self.keyword_dict:
            self.emotion_dict[keyword] = new_emotion
            self.save_csv()  # Persist changes
            print(f"Keyword '{keyword}' emotion updated to '{new_emotion}'.")
        else:
            print(f"Keyword '{keyword}' does not exist in the CSV file.")

    def add_association(self, new_association):
        if self.current_keyword is not None:
            if self.current_keyword in self.keyword_dict:
                self.keyword_dict[self.current_keyword].append(new_association)
            else:
                # If keyword is missing, create a new row.
                self.keyword_dict[self.current_keyword] = [new_association]
            self.save_csv()  # Persist changes

    def save_csv(self):
        with open(self.csv_file_path, 'w', encoding='gbk', newline='') as file:
            fieldnames = ['keyword', 'association', 'emotion']
            csv_writer = csv.DictWriter(file, fieldnames=fieldnames)
            csv_writer.writeheader()
            for keyword, association in self.keyword_dict.items():
                csv_writer.writerow({'keyword': keyword, 'association': '，'.join(association),'emotion': self.emotion_dict.get(keyword, "")})


    def get_association(self, keyword):
        if keyword in self.keyword_dict:
            self.current_keyword = keyword
            return self.keyword_dict[keyword]
        else:
            return []

    def delete_association(self, association_to_delete):
        if self.current_keyword is not None:
            if self.current_keyword in self.keyword_dict:
                if association_to_delete in self.keyword_dict[self.current_keyword]:
                    self.keyword_dict[self.current_keyword].remove(association_to_delete)
                    self.save_csv()

    def update_association(self, old_association, new_association):
        if self.current_keyword is not None:
            if self.current_keyword in self.keyword_dict:
                if old_association in self.keyword_dict[self.current_keyword]:
                    index = self.keyword_dict[self.current_keyword].index(old_association)
                    self.keyword_dict[self.current_keyword][index] = new_association
                    self.save_csv()

    def search_keyword_fuzzy(self, search_query, threshold=60):
        """
    Use fuzzy matching to find keywords.
    :param search_query: string to search
    :param threshold: fuzzy matching threshold (default 80)
    :return: matched keyword list
        """
        matches = process.extractBests(search_query, self.keyword_dict.keys(), score_cutoff=threshold)
        if not matches:
            return []

        matched_keywords = [match[0] for match in matches]
        return matched_keywords

    def delect_emotion(self,keyword):
        score = self.emotion_dict[keyword]
        return score

def find_most_similar(query, target_list, threshold=8):
    """
    Use fuzzy matching to find the closest list element.
    :param query: string to search
    :param target_list: list of candidates
    :param threshold: fuzzy matching threshold (default 80)
    :return: best match and similarity score
    """
    print(query,target_list)
    best_match, score = process.extractOne(query, target_list, score_cutoff=threshold)

    if best_match is not None:
        return best_match, score
    else:
        return "None", 0

def study_from_bilibili(bv: str, keyword: str, emotion: int = 0):
    bv_title = tool.search_for_song.search_bilibili(bv)
    manager = KeywordAssociationManager('csv/keyword_dict.csv')
    manager.add_keyword(keyword)
    manager.update_emotion(keyword, emotion)
    manager.get_association(keyword)
    tool.Fast_Whisper.stt(model_path="faster-whisper-webui/Models/faster-whisper/large-v2",input_path=os.path.join(project_root,f"download/{bv_title}.wav"),output_path=os.path.join(project_root,f"chroma_database/database/{keyword}"))
    manager.add_association(bv_title)
    chroma_database.make_db(text_path=os.path.join(project_root, f"chroma_database/database/{keyword}/{bv_title}.txt"), persist_directory=os.path.join(project_root, f"chroma_database/database/{keyword}"), chunk_size=100)

def study_from_youtube(video_id: str, keyword: str, emotion: int, audio_path: str | None = None):
    title = tool.search_for_song.search_youtube_title(video_id) or video_id
    manager = KeywordAssociationManager('csv/keyword_dict.csv')
    manager.add_keyword(keyword)
    manager.update_emotion(keyword, emotion)
    manager.get_association(keyword)
    if audio_path is None:
        audio_path = os.path.join(project_root, f"download/{title}.wav")
    tool.Fast_Whisper.stt(
        model_path="faster-whisper-webui/Models/faster-whisper/large-v2",
        input_path=audio_path,
        output_path=os.path.join(project_root, f"chroma_database/database/{keyword}"),
    )
    manager.add_association(title)
    chroma_database.make_db(
        text_path=os.path.join(project_root, f"chroma_database/database/{keyword}/{title}.txt"),
        persist_directory=os.path.join(project_root, f"chroma_database/database/{keyword}"),
        chunk_size=100,
    )

def study_from_txt(keyword: str, emotion: int = 0, txt_name: str = ""):
    manager = KeywordAssociationManager('csv/keyword_dict.csv')
    manager.add_keyword(keyword)
    manager.update_emotion(keyword,emotion)
    manager.get_association(keyword)
    manager.add_association(txt_name)
    chroma_database.make_db(text_path=os.path.join(project_root, f"chroma_database/text/{txt_name}.txt"),
                            persist_directory=os.path.join(project_root, f"chroma_database/database/{keyword}"),
                            chunk_size=100)

def detect_for_keyword(content):
    manager = KeywordAssociationManager('csv/keyword_dict.csv')
    matched_keywords = manager.search_keyword_fuzzy(content)
    if matched_keywords:
        print(f"Fuzzy-matched keywords: {matched_keywords}")
        for keyword in matched_keywords:
            associations = manager.get_association(keyword)
            print(f"{keyword} associations: {associations}")
            most_similar_text, similarity_score = find_most_similar(content,associations)
            if most_similar_text:
                print(f"Most similar text: {most_similar_text}")
                print(f"Similarity score: {similarity_score}")
                score = int(manager.delect_emotion(keyword))
                return keyword,score
            else:
                print(f"No elements exceeded the similarity threshold for '{content}'.")
                return "None","None"
    else:
        print("Normal conversation detected; no keyword found.")
        return "None","None"

def search_from_memory(content):
    keyword,score = detect_for_keyword(content)
    result = chroma_database.search_in_db(f"chroma_database/database/{keyword}", content, k_lin=2)
    if result:
        return keyword,score,result
    else:
        return "None","None","None"

if __name__ == '__main__':
    project_root = os.path.dirname(os.path.abspath(__file__))
    please = input("1. BiliBili video 2. YouTube video 3. Text learning")
    keyword = input("Enter a keyword for this learning session:")
    output_dir = f"chroma_database/database/{keyword}"
    os.makedirs(output_dir, exist_ok=True)
    if please == "1":
        bv = input("Enter the BiliBili BV ID to study:")
        study_from_bilibili(bv=bv,keyword=keyword)
    elif please == "2":
        video_id = input("Enter the YouTube video ID to study:")
        study_from_youtube(video_id=video_id, keyword=keyword, emotion=0)
    elif please == "3":
        txt_name = input("Enter the text name:")
        study_from_txt(keyword,txt_name)
    # print(search_from_memory("What is the meme about Guinaifen in real life?"))
