import re
from collections import Counter

import numpy as np
import pandas as pd
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report
import json
import os
from pathlib import Path

from utils.paths import get_config_path

try:
    from textblob import TextBlob
    _HAS_TEXTBLOB = True
except Exception:
    _HAS_TEXTBLOB = False

try:
    from wordcloud import WordCloud
    _HAS_WORDCLOUD = True
except Exception:
    WordCloud = None
    _HAS_WORDCLOUD = False

STOPWORDS = {
    'the', 'a', 'an', 'and', 'or', 'is', 'are', 'to', 'of', 'in', 'for',
    'that', 'this', 'it', 'i', 'you', 'we', 'me', 'he', 'she', 'on', 'at',
    'by', 'with', 'from', 'as', 'not', 'be', 'have', 'has', 'had', 'do',
    'does', 'did', 'will', 'would', 'can', 'could', 'should', 'if', 'then',
    'so', 'but', 'because', 'about', 'into', 'out', 'up', 'over', 'under',
    'your', 'our', 'their', 'them', 'more', 'most', 'some', 'any', 'all',
    'just', 'very', 'also', 'll', 've', 're', 'm', 's', 't'
}

POSITIVE_WORDS = {
    'good', 'great', 'love', 'happy', 'nice', 'helpful', 'excellent', 'support',
    'reliable', 'fast', 'easy', 'comfortable', 'thank', 'thanks', 'positive',
    'best', 'win', 'allow', 'available', 'sure'
}

NEGATIVE_WORDS = {
    'expensive', 'price', 'cost', 'high', 'slow', 'issue', 'problem', 'risk',
    'difficult', 'hard', 'delay', 'not', 'never', 'donot', 'don', "don't",
    'cannot', 'fail', 'worry', 'worried', 'bad', 'dislike', 'worst', 'doubt'
}


def preprocess_text(text: str) -> str:
    if text is None or (isinstance(text, float) and text != text):
        return ""

    text = str(text).lower()
    text = re.sub(r"https?://\S+|www\.\S+", "", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def build_word_frequencies(texts, top_n=40):
    words = []
    for text in texts:
        for word in str(text).split():
            if len(word) > 2 and word not in STOPWORDS:
                words.append(word)
    counter = Counter(words)
    return counter.most_common(top_n)


def build_topic_model(texts, n_topics=5, n_top_words=7):
    vectorizer = TfidfVectorizer(
        stop_words=list(STOPWORDS),
        max_features=2000,
        ngram_range=(1, 2),
        min_df=3
    )
    matrix = vectorizer.fit_transform(texts)
    lda = LatentDirichletAllocation(
        n_components=n_topics,
        random_state=42,
        learning_method='batch'
    )
    lda.fit(matrix)

    terms = vectorizer.get_feature_names_out()
    topic_terms = []
    for topic_id, topic in enumerate(lda.components_):
        top_indices = topic.argsort()[:-n_top_words - 1:-1]
        topic_terms.append(
            {
                'Topic': f'Topic {topic_id + 1}',
                'Top Terms': ", ".join(terms[i] for i in top_indices)
            }
        )

    topic_distribution = np.argmax(lda.transform(matrix), axis=1)
    topic_counts = Counter(topic_distribution)
    distribution = [
        {'Topic': f'Topic {topic_id + 1}', 'Count': topic_counts.get(topic_id, 0)}
        for topic_id in range(n_topics)
    ]

    return topic_terms, distribution


def assign_topics_to_texts(texts, n_topics=5, n_top_words=4):
    """Assign an LDA topic label to each text."""
    texts = list(texts)
    assignments = ['Unassigned'] * len(texts)
    labels = ['Unassigned'] * len(texts)

    cleaned = [preprocess_text(text) for text in texts]
    valid_pairs = [(index, text) for index, text in enumerate(cleaned) if text]

    if len(valid_pairs) < 15:
        return assignments, labels, [], []

    valid_indices = [pair[0] for pair in valid_pairs]
    valid_texts = [pair[1] for pair in valid_pairs]
    topic_count = min(n_topics, max(2, len(valid_texts) // 25))

    vectorizer = TfidfVectorizer(
        stop_words=list(STOPWORDS),
        max_features=2000,
        ngram_range=(1, 2),
        min_df=3,
    )
    matrix = vectorizer.fit_transform(valid_texts)
    lda = LatentDirichletAllocation(
        n_components=topic_count,
        random_state=42,
        learning_method='batch',
    )
    lda.fit(matrix)

    terms = vectorizer.get_feature_names_out()
    topic_labels_map = {}
    topic_terms = []
    for topic_id, topic in enumerate(lda.components_):
        top_indices = topic.argsort()[:-n_top_words - 1:-1]
        top_terms = ", ".join(terms[index] for index in top_indices)
        topic_labels_map[topic_id] = f"Topic {topic_id + 1}: {top_terms}"
        topic_terms.append(
            {
                'Topic': f"Topic {topic_id + 1}",
                'Top Terms': top_terms,
            }
        )

    topic_ids = np.argmax(lda.transform(matrix), axis=1)
    topic_counts = Counter(topic_ids)
    distribution = [
        {
            'Topic': f"Topic {topic_id + 1}",
            'Count': topic_counts.get(topic_id, 0),
        }
        for topic_id in range(topic_count)
    ]

    for row_index, topic_id in zip(valid_indices, topic_ids):
        assignments[row_index] = f"Topic {topic_id + 1}"
        labels[row_index] = topic_labels_map[topic_id]

    return assignments, labels, topic_terms, distribution


def train_objection_classifier(texts, labels, top_labels=8):
    df = (
        pd.DataFrame({'text': texts, 'label': labels})
        .dropna(subset=['text', 'label'])
    )
    df['text'] = df['text'].astype(str)
    df['label'] = df['label'].astype(str)

    if df['label'].nunique() < 2 or len(df) < 30:
        return None

    label_order = df['label'].value_counts().nlargest(top_labels).index.tolist()
    if len(label_order) < 2:
        return None

    df = df[df['label'].isin(label_order)].reset_index(drop=True)

    X_train, X_test, y_train, y_test = train_test_split(
        df['text'], df['label'], test_size=0.2, random_state=42, stratify=df['label']
    )

    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(
            stop_words=list(STOPWORDS),
            max_features=3000,
            ngram_range=(1, 2)
        )),
        ('clf', LogisticRegression(
            max_iter=500,
            class_weight='balanced',
            random_state=42,
            n_jobs=-1
        ))
    ])

    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)

    report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
    accuracy = accuracy_score(y_test, y_pred)

    report_df = pd.DataFrame(report).transpose().round(3)
    report_df = report_df.drop(columns=[c for c in report_df.columns if c not in {'precision', 'recall', 'f1-score', 'support'}], errors='ignore')

    features = pipeline.named_steps['tfidf'].get_feature_names_out()
    coef = np.abs(pipeline.named_steps['clf'].coef_).sum(axis=0)
    top_features = sorted(
        zip(features, coef), key=lambda x: x[1], reverse=True
    )[:12]
    top_feature_df = pd.DataFrame(top_features, columns=['Feature', 'Importance'])

    sample_df = (
        pd.DataFrame({'text': X_test, 'Actual': y_test, 'Predicted': y_pred})
        .reset_index(drop=True)
        .head(8)
    )

    cm = None
    try:
        from sklearn.metrics import confusion_matrix
        cm = confusion_matrix(y_test, y_pred, labels=label_order)
    except Exception:
        cm = None

    return {
        'model': pipeline,
        'accuracy': accuracy,
        'report_df': report_df,
        'top_features': top_feature_df,
        'sample_predictions': sample_df,
        'confusion_matrix': cm,
        'confusion_labels': label_order
    }


def predict_sentiment(text: str):
    text = preprocess_text(text)
    if not text:
        return 'Neutral', 0.0

    polarity = None
    if _HAS_TEXTBLOB:
        try:
            polarity = TextBlob(text).sentiment.polarity
        except Exception:
            polarity = None

    if polarity is None:
        words = set(text.split())
        score = sum(1 for token in words if token in POSITIVE_WORDS)
        score -= sum(1 for token in words if token in NEGATIVE_WORDS)
        polarity = float(score) / max(len(words), 1)

    if polarity > 0.15:
        label = 'Positive'
    elif polarity < -0.15:
        label = 'Negative'
    else:
        label = 'Neutral'

    return label, round(polarity, 3)




def load_subclass_rules(path=None):
    """Load subclass rules JSON. Default path points to the project config folder."""
    if path is None:
        path = get_config_path('subclass_rules.json')

    path = Path(path) if not isinstance(path, Path) else path

    if not path.exists():
        return None

    with open(path, 'r', encoding='utf-8') as f:
        rules = json.load(f)
    return rules


CLASS_LABEL_ALIASES = {
    'documentation': 'Documentation Concern',
    'price': 'Price Concern',
    'processing time': 'Processing Time Concern',
    'trust': 'Trust Issue',
    'lack of understanding': 'Lack Of Understanding',
    'convenience / location': 'Location Concern',
    'location concern': 'Location Concern',
    'risk / guarantee concerns': 'Risk / Guarantee Concern',
    'risk / guarantee concern': 'Risk / Guarantee Concern',
    'employme - out of scope': 'Employment - Out of Scope',
    'employment - out of scope': 'Employment - Out of Scope',
    'comparison / competitor claim': 'Comparison / Competitor Claim',
    'others': 'Others',
}


def _resolve_rule_class_key(label, class_keys):
    normalized = CLASS_LABEL_ALIASES.get(str(label).strip().lower())
    if normalized and normalized in class_keys:
        return normalized

    label_lower = str(label).lower()
    for key in class_keys:
        key_lower = key.lower()
        if label_lower == key_lower or label_lower in key_lower or key_lower in label_lower:
            return key
    return None


def apply_subclass_rules(texts, labels, rules, class_name=None):
    """Apply rule-based subclass matching.

    texts: iterable of raw texts (list or Series) aligned with labels
    labels: iterable of main class labels aligned with texts
    rules: dict loaded from subclass_rules.json
    class_name: if provided, restrict to that main class

    Returns a dict with per-class summaries and a DataFrame of assignments.
    """
    if rules is None:
        return None

    texts = list(texts)
    labels = list(labels)
    records = []
    classes_rules = rules.get('classes', {})

    class_keys = list(classes_rules.keys())
    label_to_key = {}
    for lab_val in set(labels):
        label_to_key[lab_val] = _resolve_rule_class_key(lab_val, class_keys)

    for text, lab in zip(texts, labels):
        if class_name and lab != class_name:
            continue
        assigned = 'Unspecified'
        rule_key = label_to_key.get(lab)
        cls_rules = classes_rules.get(rule_key, {}) if rule_key else {}
        subclasses = cls_rules.get('subclasses', {}) if cls_rules else {}
        text_l = str(text).lower()
        # first match exact_phrases
        for sub_name, sub_rules in subclasses.items():
            for phrase in sub_rules.get('exact_phrases', []) or []:
                if phrase and phrase in text_l:
                    assigned = sub_name
                    break
            if assigned != 'Unspecified':
                break
        # if not matched, check keywords
        if assigned == 'Unspecified':
            for sub_name, sub_rules in subclasses.items():
                for kw in sub_rules.get('keywords', []) or []:
                    if kw and kw in text_l.split():
                        assigned = sub_name
                        break
                if assigned != 'Unspecified':
                    break

        records.append({'text': text, 'class': lab, 'subclass': assigned})

    df_assign = pd.DataFrame(records)
    summary = {}
    if not df_assign.empty:
        group = df_assign.groupby(['class', 'subclass']).size().reset_index(name='count')
        for cls in group['class'].unique():
            sub_df = group[group['class'] == cls][['subclass', 'count']].sort_values('count', ascending=False)
            summary[cls] = sub_df.to_dict(orient='records')

    return {'assignments': df_assign, 'summary': summary}
