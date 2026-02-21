"""
Twitter/X Scraper для валидации SaaS идей

Собирает твиты, анализирует engagement и находит проблемы пользователей
"""

import tweepy
import pandas as pd
from datetime import datetime, timedelta
import json
import re
from collections import Counter
import time


class TwitterSaaSValidator:
    def __init__(self, bearer_token):
        """
        Инициализация Twitter API v2 клиента
        
        Для получения bearer_token:
        1. Перейдите на https://developer.twitter.com/en/portal/dashboard
        2. Создайте новое приложение
        3. Получите Bearer Token из раздела "Keys and tokens"
        """
        self.client = tweepy.Client(bearer_token=bearer_token)
    
    def search_tweets(self, query, max_results=100, days_back=7):
        """
        Поиск твитов по запросу
        
        Args:
            query: поисковый запрос (может включать операторы)
            max_results: максимальное количество твитов (10-100 за запрос)
            days_back: сколько дней назад искать
            
        Returns:
            DataFrame с твитами
        """
        tweets_data = []
        
        # Временной фильтр
        start_time = datetime.utcnow() - timedelta(days=days_back)
        
        print(f"Поиск твитов по запросу: {query}")
        print(f"Период: последние {days_back} дней")
        
        try:
            # Поиск с метриками
            tweets = self.client.search_recent_tweets(
                query=query,
                max_results=max_results,
                start_time=start_time,
                tweet_fields=['created_at', 'public_metrics', 'author_id', 'lang'],
                expansions=['author_id'],
                user_fields=['username', 'name', 'public_metrics']
            )
            
            if not tweets.data:
                print("Твиты не найдены")
                return pd.DataFrame()
            
            # Создаем словарь пользователей
            users = {user.id: user for user in tweets.includes.get('users', [])}
            
            for tweet in tweets.data:
                user = users.get(tweet.author_id)
                
                tweet_info = {
                    'id': tweet.id,
                    'text': tweet.text,
                    'created_at': tweet.created_at,
                    'lang': tweet.lang,
                    'likes': tweet.public_metrics['like_count'],
                    'retweets': tweet.public_metrics['retweet_count'],
                    'replies': tweet.public_metrics['reply_count'],
                    'impressions': tweet.public_metrics.get('impression_count', 0),
                    'engagement': tweet.public_metrics['like_count'] + 
                                 tweet.public_metrics['retweet_count'] + 
                                 tweet.public_metrics['reply_count'],
                    'author_username': user.username if user else None,
                    'author_name': user.name if user else None,
                    'author_followers': user.public_metrics['followers_count'] if user else 0,
                    'url': f"https://twitter.com/i/web/status/{tweet.id}"
                }
                
                tweets_data.append(tweet_info)
            
            print(f"✅ Найдено {len(tweets_data)} твитов")
            
        except tweepy.errors.TweepyException as e:
            print(f"❌ Ошибка Twitter API: {e}")
            return pd.DataFrame()
        
        return pd.DataFrame(tweets_data)
    
    def search_multiple_keywords(self, keywords, max_results_per_keyword=50, days_back=7):
        """
        Поиск по нескольким ключевым словам
        """
        all_tweets = []
        
        for keyword in keywords:
            print(f"  Поиск: {keyword}")
            tweets_df = self.search_tweets(
                query=keyword,
                max_results=max_results_per_keyword,
                days_back=days_back
            )
            
            if not tweets_df.empty:
                tweets_df['keyword'] = keyword
                all_tweets.append(tweets_df)
            
            # Задержка между запросами (rate limit)
            time.sleep(2)
        
        if not all_tweets:
            return pd.DataFrame()
        
        combined = pd.concat(all_tweets, ignore_index=True)
        
        # Удаляем дубликаты по ID
        combined = combined.drop_duplicates(subset=['id'])
        
        return combined
    
    def find_pain_points(self, tweets_df):
        """
        Анализ болевых точек в твитах
        """
        if tweets_df.empty:
            return pd.DataFrame()
        
        pain_keywords = [
            'struggling', 'frustrated', 'annoying', 'waste time',
            'difficult', 'problem', 'issue', 'broken', 'hate',
            'wish', 'need', 'missing', 'slow', 'expensive',
            'complicated', 'confusing'
        ]
        
        pain_tweets = []
        
        for _, tweet in tweets_df.iterrows():
            text_lower = tweet['text'].lower()
            
            for keyword in pain_keywords:
                if keyword in text_lower:
                    pain_tweets.append({
                        'tweet_id': tweet['id'],
                        'text': tweet['text'],
                        'keyword': keyword,
                        'engagement': tweet['engagement'],
                        'created_at': tweet['created_at'],
                        'url': tweet['url']
                    })
                    break  # Один твит считаем только один раз
        
        return pd.DataFrame(pain_tweets)
    
    def analyze_hashtags(self, tweets_df):
        """
        Анализ популярных хештегов
        """
        if tweets_df.empty:
            return Counter()
        
        hashtags = []
        for text in tweets_df['text']:
            found_hashtags = re.findall(r'#(\w+)', text)
            hashtags.extend([h.lower() for h in found_hashtags])
        
        return Counter(hashtags)
    
    def analyze_mentions(self, tweets_df):
        """
        Анализ упоминаний (@mentions) - часто это конкуренты
        """
        if tweets_df.empty:
            return Counter()
        
        mentions = []
        for text in tweets_df['text']:
            found_mentions = re.findall(r'@(\w+)', text)
            mentions.extend([m.lower() for m in found_mentions])
        
        return Counter(mentions)
    
    def get_user_tweets(self, username, max_results=100):
        """
        Получить твиты конкретного пользователя
        
        Полезно для анализа конкурентов или thought leaders
        """
        try:
            user = self.client.get_user(username=username)
            
            if not user.data:
                print(f"Пользователь @{username} не найден")
                return pd.DataFrame()
            
            user_id = user.data.id
            
            tweets = self.client.get_users_tweets(
                id=user_id,
                max_results=max_results,
                tweet_fields=['created_at', 'public_metrics']
            )
            
            if not tweets.data:
                return pd.DataFrame()
            
            tweets_data = []
            for tweet in tweets.data:
                tweets_data.append({
                    'text': tweet.text,
                    'created_at': tweet.created_at,
                    'likes': tweet.public_metrics['like_count'],
                    'retweets': tweet.public_metrics['retweet_count'],
                    'replies': tweet.public_metrics['reply_count'],
                    'engagement': tweet.public_metrics['like_count'] + 
                                 tweet.public_metrics['retweet_count'] + 
                                 tweet.public_metrics['reply_count']
                })
            
            return pd.DataFrame(tweets_data)
            
        except tweepy.errors.TweepyException as e:
            print(f"❌ Ошибка: {e}")
            return pd.DataFrame()
    
    def generate_report(self, keywords, output_file='twitter_analysis.json'):
        """
        Генерирует полный отчет для валидации идеи
        """
        print(f"\n{'='*60}")
        print(f"Twitter/X Анализ")
        print(f"{'='*60}\n")
        
        # Собираем твиты
        tweets_df = self.search_multiple_keywords(keywords, max_results_per_keyword=100)
        
        if tweets_df.empty:
            print("❌ Твиты не найдены")
            return None, None
        
        # Анализ
        pain_points = self.find_pain_points(tweets_df)
        hashtags = self.analyze_hashtags(tweets_df)
        mentions = self.analyze_mentions(tweets_df)
        
        # Формируем отчет
        report = {
            'platform': 'Twitter/X',
            'analysis_date': datetime.now().isoformat(),
            'total_tweets': len(tweets_df),
            'keywords_searched': keywords,
            'top_tweets': tweets_df.nlargest(10, 'engagement')[
                ['text', 'engagement', 'likes', 'retweets', 'url']
            ].to_dict('records'),
            'pain_points_count': len(pain_points),
            'top_pain_keywords': pain_points['keyword'].value_counts().head(10).to_dict() if len(pain_points) > 0 else {},
            'top_hashtags': dict(hashtags.most_common(20)),
            'top_mentions': dict(mentions.most_common(20)),
            'engagement_stats': {
                'avg_likes': float(tweets_df['likes'].mean()),
                'avg_retweets': float(tweets_df['retweets'].mean()),
                'avg_replies': float(tweets_df['replies'].mean()),
                'total_engagement': int(tweets_df['engagement'].sum())
            },
            'language_distribution': tweets_df['lang'].value_counts().to_dict()
        }
        
        # Сохраняем отчет
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Отчет сохранен: {output_file}")
        
        # Выводим краткую сводку
        print(f"\n📊 Краткая сводка:")
        print(f"- Найдено твитов: {len(tweets_df)}")
        print(f"- Pain points: {len(pain_points)}")
        print(f"- Средний engagement: {report['engagement_stats']['avg_likes']:.1f} likes")
        print(f"- Общий engagement: {report['engagement_stats']['total_engagement']}")
        
        if hashtags:
            print(f"\n🔥 Топ хештегов:")
            for tag, count in hashtags.most_common(10):
                print(f"  #{tag}: {count}")
        
        if mentions:
            print(f"\n👤 Топ упоминаний (возможные конкуренты):")
            for mention, count in mentions.most_common(10):
                print(f"  @{mention}: {count}")
        
        return report, tweets_df


class TwitterAdvancedSearch:
    """
    Расширенные поисковые запросы для Twitter
    """
    
    @staticmethod
    def build_pain_query(topic):
        """
        Строит запрос для поиска болевых точек
        """
        pain_words = ['struggling', 'frustrated', 'annoying', 'hate', 'problem', 'issue']
        # Используем OR оператор
        pain_query = f'{topic} ({" OR ".join(pain_words)})'
        return pain_query
    
    @staticmethod
    def build_solution_query(topic):
        """
        Строит запрос для поиска запросов на решение
        """
        solution_words = ['how to', 'best way', 'recommend', 'looking for', 'need help', 'advice']
        solution_query = f'{topic} ({" OR ".join(solution_words)})'
        return solution_query
    
    @staticmethod
    def build_competitor_query(topic, competitors):
        """
        Строит запрос для анализа конкурентов
        """
        # Ищем упоминания конкурентов с мнениями
        competitor_mentions = ' OR '.join([f'@{comp}' for comp in competitors])
        query = f'{topic} ({competitor_mentions})'
        return query
    
    @staticmethod
    def build_willingness_to_pay_query(topic):
        """
        Строит запрос для поиска готовности платить
        """
        payment_words = ['worth it', 'price', 'expensive', 'cheap', 'paying for', 'subscription']
        query = f'{topic} ({" OR ".join(payment_words)})'
        return query


def main():
    """
    Пример использования Twitter scraper
    """
    
    # ВАЖНО: Замените на ваш Bearer Token
    BEARER_TOKEN = "ваш_bearer_token"
    
    scraper = TwitterSaaSValidator(BEARER_TOKEN)
    
    # Пример 1: Простой поиск
    print("=" * 60)
    print("ПРИМЕР 1: Поиск по ключевым словам")
    print("=" * 60)
    
    keywords = [
        'email marketing tool',
        'email automation',
        'newsletter platform',
        'cold email software'
    ]
    
    report, tweets = scraper.generate_report(keywords)
    
    if tweets is not None and not tweets.empty:
        tweets.to_csv('twitter_tweets.csv', index=False, encoding='utf-8')
    
    # Пример 2: Расширенный поиск болевых точек
    print("\n" + "=" * 60)
    print("ПРИМЕР 2: Поиск болевых точек")
    print("=" * 60)
    
    topic = "team collaboration"
    pain_query = TwitterAdvancedSearch.build_pain_query(topic)
    
    pain_tweets = scraper.search_tweets(pain_query, max_results=100, days_back=7)
    
    if not pain_tweets.empty:
        pain_tweets.to_csv('twitter_pain_points.csv', index=False)
        print(f"\n✅ Найдено {len(pain_tweets)} твитов с болевыми точками")
    
    # Пример 3: Анализ конкурентов
    print("\n" + "=" * 60)
    print("ПРИМЕР 3: Анализ конкурентов")
    print("=" * 60)
    
    competitors = ['notion', 'airtable', 'asana', 'monday']
    competitor_query = TwitterAdvancedSearch.build_competitor_query('productivity', competitors)
    
    competitor_tweets = scraper.search_tweets(competitor_query, max_results=100)
    
    if not competitor_tweets.empty:
        competitor_tweets.to_csv('twitter_competitors.csv', index=False)
        
        # Анализ sentiment к конкурентам
        mentions = scraper.analyze_mentions(competitor_tweets)
        print("\nУпоминания конкурентов:")
        for mention, count in mentions.most_common(10):
            print(f"  @{mention}: {count} раз")
    
    # Пример 4: Анализ thought leaders
    print("\n" + "=" * 60)
    print("ПРИМЕР 4: Анализ thought leaders")
    print("=" * 60)
    
    thought_leaders = ['naval', 'levelsio', 'paulg', 'patio11']
    
    for leader in thought_leaders:
        print(f"\nАнализ @{leader}...")
        user_tweets = scraper.get_user_tweets(leader, max_results=50)
        
        if not user_tweets.empty:
            avg_engagement = user_tweets['engagement'].mean()
            print(f"  Средний engagement: {avg_engagement:.1f}")
            print(f"  Топ твит: {user_tweets.nlargest(1, 'engagement')['text'].values[0][:100]}...")


if __name__ == "__main__":
    main()
