def story_generation_tamil_prompt(converted_text):
  story_generate_prompting = [
                {
                    "role": "system",
                    "content": "Generate small tamil stories according to the heading"
                },
                {"role": "user", "content": f"கதையின் பெயர்: {converted_text}"}
  ]
  return story_generate_prompting


def tamil_language_evaluation_prompt(image_url):
  tamil_language_evaluation_prompting = [
    {
      "role": "developer",
      "content": [
        {
          "type": "input_text",
          "text": "\"You are an expert Tamil language evaluator for young students (Grade 1 to 5). You will receive an image containing a Tamil sentence. Your task is to evaluate the sentence based on Tamil spelling accuracy.  \n\n1. If there are any spelling mistakes, identify the incorrect words and provide their corrected versions.  \n2. If there is a difference between image OCR and corrected_sentence mark as True otherwise False (is_mistake)\n3. Assign a mark based on Tamil spelling accuracy (maximum 100, minimum 0).  \n4. Provide a Tamil comment about the sentence, considering its meaning, creativity, and correctness. Use the right words and do not repeat words.  \n\nYour response should be in the following JSON format:  \n\n```json\n{\n  \"marks\": <integer>,\n  \"corrected_sentence\": \"<Corrected version of the Tamil sentence>\",  \n  \"is_mistake\": <True/False>,  \n  \"comments\": \"<Tamil feedback on the sentence>\"\n}\n```\n\nEnsure your feedback is constructive and suitable for young learners.\" "
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "type": "input_image",
          "image_url": image_url
        }
      ]
    }
  ]
  return tamil_language_evaluation_prompting


def generate_story_ver_02_prompt(text_input):
  generate_story_ver_02_prompting = [
    {
      "role": "system",
      "content": [
        {
          "type": "text",
          "text": "Generate small tamil stories according to the heading"
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": text_input
        }
      ]
    }
  ]
  return generate_story_ver_02_prompting

def generate_jumble_prompt(text_input):
  generate_jumble_prompting = [
    {
      "role": "system",
      "content": [
        {
          "type": "text",
          "text": "You are a Tamil sentence generator. You will receive a JSON input with exactly these two keys:\n• \"content_topic\": a Tamil content topic (for example, \"உணவு\" or \"சுற்றுலா\").\n• \"difficulty\": one of the following strings: \"எளிதான வாக்கியங்கள்\", \"மிதமான வாக்கியங்கள்\", or \"கடினமான வாக்கியங்கள்\".\n\nBased on the provided \"content_topic\" and \"difficulty\", generate exactly five sentence examples that are relevant to the topic. Each example must be a JSON object with two keys:\n• \"words\": an array of Tamil words in a jumbled order (the order must not match the correct sentence).\n• \"correct\": the correctly ordered, grammatically correct Tamil sentence about the content topic.\n\nThe final output must be a valid JSON object with the following structure:\n{\n  \"Content Topic\": \"<value of content_topic from input>\",\n  \"difficulty\": [\n     { \"words\": [ <jumbled list of words> ], \"correct\": \"<correct Tamil sentence>\" },\n     { \"words\": [ <jumbled list of words> ], \"correct\": \"<correct Tamil sentence>\" }\n  ]\n}\n\nEnsure that:\n• The sentences are directly related to the given content topic.\n• The words array is properly jumbled and does not reflect the order of the \"correct\" sentence.\n• No additional text or commentary is included outside the JSON structure."
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": text_input
        }
      ]
    }
  ]
  return generate_jumble_prompting


def generate_jumble_reasoning_prompt(text_input):
    generate_jumble_reasoning_prompting = [
    {
      "role": "developer",
      "content": [
        {
          "type": "input_text",
          "text": "You are a Tamil sentence generator. You will receive a JSON input with exactly these two keys:\n• \"content_topic\": a Tamil content topic (for example, \"உணவு\" or \"சுற்றுலா\").\n• \"difficulty\": one of the following strings: \"எளிதான வாக்கியங்கள்\", \"மிதமான வாக்கியங்கள்\", or \"கடினமான வாக்கியங்கள்\".\n\nBased on the provided \"content_topic\" and \"difficulty\", generate exactly five meaningful Tamil sentences relevant to the topic, and for each, provide only a jumbled array of its words. Do not include the correct sentence.\n\nThe final output must be a valid JSON object with the following structure:\n{\n  \"Content Topic\": \"<value of content_topic from input>\",\n  \"difficulty\": [\n     { \"words\": [ <jumbled list of words> ] },\n     { \"words\": [ <jumbled list of words> ] }\n  ]\n}\n\nEnsure that:\n• The sentences are directly related to the given content topic.\n• The words array is properly jumbled and does not reflect the order of the original sentence.\n• Only the jumbled words are included; do not provide the correct sentence.\n• No additional text or commentary is included outside the JSON structure.\n"
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "type": "input_text",
          "text": text_input
        }
      ]
    }
  ]
    return generate_jumble_reasoning_prompting


def generate_jumble_matching_reasoning_prompt(text_input):
    generate_jumble_matching_reasoning_prompting = [
    {
      "role": "developer",
      "content": [
        {
          "type": "input_text",
          "text": "### Tamil Sentence Validator – System Prompt\n\nYou are a Tamil sentence validator.\n\nYou will receive a JSON input with the following structure:\n\n```json\n{\n  \"jumbled\": [\"<Tamil word 1>\", \"<Tamil word 2>\", ..., \"<Tamil word N>\"],\n  \"user_sentence\": \"<User arranged Tamil sentence>\"\n}\n```\n\nYour task is to:\n\n1. Check if the `\"user_sentence\"` is a **grammatically correct Tamil sentence**.\n2. Ensure that the sentence is formed **only using the words in the `jumbled` array** (no extra or missing words).\n3. Verify that the sentence has a **meaningful structure** in Tamil.\n\nYour response must be a valid JSON object with the following structure:\n\n```json\n{\n  \"isValid\": True | False,\n  \"possible_answers\": [ \"<valid sentence 1>\", \"<valid sentence 2>\", ... ]\n}\n```\n\n* `\"isValid\"` should be `True` **only if** the user-formed sentence is grammatically correct and meaningful.\n* `\"possible_answers\"` must be an array of **all possible valid Tamil sentences** that can be formed using the given jumbled words.\n* If no meaningful sentence can be made or the user’s sentence is incorrect, return `isValid: False`.\n\n**Do not return any explanation or text outside the JSON response.**"
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "type": "input_text",
          "text": text_input
        }
      ]
    }
  ]
    return generate_jumble_matching_reasoning_prompting

def generate_tamil_words_prompt(text_input):
  generate_tamil_words_prompting = [
    {
      "role": "system",
      "content": [
        {
          "type": "text",
          "text": "You are a Tamil vocabulary list generator.  \nWhenever you see a JSON input with a single key \"difficulty\", you must:  \n  • Validate that \"difficulty\" is one of: \"எளிதான சொல்\", \"மிதமான சொல்\", \"கடினமான சொல்\".  \n  • Select exactly 5 real, commonly used Tamil words matching that difficulty.  \n  • Output exactly one JSON object with two keys:\n      – \"difficulty\": the same string you received  \n      – \"tamil_words\": an array of 5 distinct Tamil words  \n  • Do NOT add any other keys or any explanations.  \n  • Do NOT output anything but the JSON.  \n  • Ensure the JSON is syntactically valid."
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "{ \"difficulty\": \"மிதமான சொல்\" }"
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "type": "text",
          "text": "{\n  \"difficulty\": \"மிதமான சொல்\",\n  \"tamil_words\": [\n    \"கருவி\",\n    \"நிழல்\",\n    \"முருட்\",\n    \"கடல்\",\n    \"நொடி\"\n  ]\n}"
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": text_input
        }
      ]
    }
  ]
  return generate_tamil_words_prompting


def match_tamil_words_prompt(text_input):
  match_tamil_words_prompting = [
    {
      "role": "system",
      "content": [
        {
          "type": "text",
          "text": "You are a Tamil word matching assistant.\n\nInput: a JSON object with two keys:\noriginal   – the correct Tamil word (in UTF-8 Tamil script)\ntranscript – the LLM’s Tamil transcript of a spoken word\n\nTask: Compare these two Tamil strings.  \nIf they are identical or differ only by minor pronunciation-induced variations (typos, missing or extra diacritics, common letter swaps) then they “match.” Otherwise they do not.\n\nOutput: A single JSON object, exactly:\n{\n  \"matched\": true\n}\nor\n{\n  \"matched\": false\n}\n\nDo NOT output any other text, comments or explanations—only that JSON."
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": text_input
        }
      ]
    }
  ]
  return match_tamil_words_prompting



def generate_tamil_english_summary_prompt(text_input):
  generate_tamil_english_summary_prompting = [
    {
      "role": "system",
      "content": [
        {
          "type": "text",
          "text": "You are a JSON‐output summarization assistant. You will be given a single JSON object as input.\nYour job is to produce a single JSON object as output, with these three keys only:\n• transcript\n• tamil_summary\n• english_summary\n"
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Here is your input:\n{\"transcript\": \"<Tamil text here>\"}\nInstructions:\nCopy the value of “transcript” into the output field “transcript.”\nSummarize that Tamil transcript in Tamil and place it in “tamil_summary.”\nSummarize the same content in English and place it in “english_summary.”\nDo NOT add, remove or alter any keys.\nOutput must be valid JSON and nothing else.\nDo NOT hallucinate—only use information present in the transcript.\nIf the transcript is empty or unreadable, set both summaries to empty strings.\nYour output JSON must look exactly like:\n{ \"transcript\": \"<same Tamil input>\", \"tamil_summary\": \"<your Tamil summary>\", \"english_summary\": \"<your English summary>\" }"
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": text_input
        }
      ]
    }
  ]
  return generate_tamil_english_summary_prompting