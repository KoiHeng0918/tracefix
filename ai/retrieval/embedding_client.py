import dashscope


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    response = dashscope.TextEmbedding.call(
        model="qwen3.7-text-embedding-flash",
        input=texts
    )
    if response.status_code != 200:
        raise RuntimeError(f"embedding 调用失败: {response.code} {response.message}")

    items = response.output["embeddings"]

    items.sort(key=lambda item: item["text_index"])
    
    return [item["embedding"] for item in items]