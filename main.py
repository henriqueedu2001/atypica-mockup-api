import os
import shutil
from fastapi import FastAPI, File, UploadFile, HTTPException
import os
import json
from pathlib import Path
from typing import *

app = FastAPI(
    title="Atypica API",
    description="API do Atypica para análise de provas.",
    version="1.0.0"
)

UPLOAD_DIRECTORY = "./files"

@app.post("/upload", status_code=201)
async def upload_document(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF is allowed.")

    file_path = os.path.join(UPLOAD_DIRECTORY, 'exam.pdf')

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        file.file.close()

    return {"filename": file.filename, "message": "File stored successfully"}


@app.get("/blame")
async def get_blame():
    blamings = FileManager.load_json('files/blamings.json')
    return blamings


@app.get("/extracted")
async def get_extracted():
    questions = FileManager.load_json('files/extracted_questions.json').get('questions')
    full_exam = FileManager.load_text('files/exam.txt')
    answer = {
        "questions": questions,
        "full_exam": full_exam
    }
    return answer


@app.get("/get_requirement_definition")
async def get_requirement_definition(requirement_id: str):
    requirement_text = FileManager.load_text(f'requirements/{requirement_id}.md')
    requirement_name = str.split(requirement_text, sep='\n')[0].replace('*', '')
    return {
        "requirement_id": requirement_id,
        "requirement_name": requirement_name,
        "full_markdown": requirement_text
    }


class FileManager:
    def cast_path(path: Union[str, Path]):
        if type(path) is not Path: return Path(path)
        return path
    
    
    def load_text(file_path: Path) -> str:
        casted_file_path = FileManager.cast_path(file_path)
        with open(casted_file_path, 'r', encoding='utf-8') as file:
            req_text = file.read()
            return req_text
        return
    
    
    def save_json(file_path: Path, json_content: str):
        casted_file_path = FileManager.cast_path(file_path)
        with open(casted_file_path, 'w', encoding='utf-8') as file:
            json.dump(json_content, file, ensure_ascii=False, indent=4)
        return
    
    
    def load_json(file_path: Path) -> json:
        casted_file_path = FileManager.cast_path(file_path)
        with open(casted_file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
        return