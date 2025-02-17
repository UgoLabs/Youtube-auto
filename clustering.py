from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

def cluster_topics(topics: List[str], num_clusters: int) -> List[List[str]]:
    """
    Clusters a list of topics into groups using TF-IDF and KMeans.
    Returns a list of clusters (each a list of topic strings).
    """
    if not topics:
        return []
    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform(topics)
    kmeans = KMeans(n_clusters=min(num_clusters, len(topics)), random_state=42)
    kmeans.fit(X)
    labels = kmeans.labels_
    clusters = [[] for _ in range(min(num_clusters, len(topics)))]
    for idx, label in enumerate(labels):
        clusters[label].append(topics[idx])
    return [cluster for cluster in clusters if cluster]
