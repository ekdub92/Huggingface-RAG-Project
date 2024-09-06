import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from elasticsearch import Elasticsearch, helpers
import json

# load dataset
raw_path = 'huggingface.transformers'
lines = open(raw_path, 'r').readlines()

# transfer as json
df = pd.DataFrame(lines, columns=['sentence'])
json_data = df.to_json(orient='records')
records = json.loads(json_data)

# compute TF-IDF
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(df['sentence'])

# initialize elasticsearch client
client = Elasticsearch('http://127.0.0.1:9201')

# define the index configuration with dense_vector type
index_config = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0
    },
    "mappings": {
        "properties": {
            "content": {
                "type": "text"
            },
            "content_vector": {
                "type": "dense_vector",
                "dims": tfidf_matrix.shape[1]
            }
        }
    }
}

# create the index
index_name = 'tfidf_vector_index'
client.indices.create(index=index_name, body=index_config, ignore=400)

# prepare documents for indexing
docs = [{
    "_index": index_name,
    "_source": {
        "content": line['sentence'],
        "content_vector": tfidf_matrix[index].toarray().flatten().tolist()
    }
} for index, line in enumerate(records)]

# bulk indexing the documents 
helpers.bulk(client, docs, index=index_name, raise_on_error=False)

# example vector inference 
query = "What is Transformer?"
query_vector = vectorizer.transform([query]).toarray()[0].tolist()

# define the vector similarity query 
script_query = {
    "script_score": {
        "query": {"match_all": {}},
        "script": {
            "source": "cosineSimilarity(params.query_vector, doc['content_vector']) + 1.0",
            "params": {"query_vector": query_vector}
        }
    }
}

# perform the search 
response = client.search(
    index=index_name,
    query=script_query,
    size=10,
    _source_includes=["content"]
)

# display results
for hit in response['hits']['hits']:
    print(f'Content: {hit["_source"]["content"]}, Score: {hit["_score"]}')
