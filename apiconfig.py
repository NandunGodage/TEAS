from pydantic import BaseModel

class ModelStory(BaseModel):
    user: int
    text: str

class ModelJumble(BaseModel):
    user: int
    text: dict

class ModelGenerateWords(BaseModel):
    user: int
    text: str

class ModelCheckTamilWords(BaseModel):
    user: int
    text: dict

# # Example usage of ModelJumble
# jumble_example = ModelJumble(
#     user=1,
    # text={
    #     "content_topic": "example_topic",
    #     "difficulty": "easy"
    # }
# )