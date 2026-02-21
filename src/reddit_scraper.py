"""
Reddit Scraper для валидации SaaS идей

Собирает посты и комментарии, анализирует engagement и находит проблемы пользователей
"""

import praw
import pandas as pd
from datetime import datetime, timedelta
import json
import re
from collections import Counter
import time


class RedditSaaSValidator:
    def __init__(self, client_id, client_secret, user_agent):
        """
        Инициализация Reddit API клиента
        
        Для получения credentials:
        1. Перейдите на https://www.reddit.com/prefs/apps
        2. Создайте новое приложение (script type)
        3. Получите client_id и client_secret
        
        Args:
            client_id: ID приложения (под "personal use script")
            client_secret: Secret приложения
            user_agent: Описание приложения (например, "SaaS Validator by u/yourname")
        """
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        
        # Проверка подключения
        try:
            self.reddit.user.me()
            print("✅ Reddit API подключен (read-only mode)")
        except:
            print("✅ Reddit API подключен (anonymous mode)")
    
    def search_subreddit(self, subreddit_name, query, limit=100, time_filter='month', sort='relevance'):
        """
        Поиск постов в конкретном subreddit
        
        Args:
            subreddit_name: название subreddit (без r/)
            query: поисковый запрос
            limit: максимальное количество постов
            time_filter: 'hour', 'day', 'week', 'month', 'year', 'all'
            sort: 'relevance', 'hot', 'top', 'new', 'comments'
            
        Returns:
            DataFrame с постами
        """
        posts_data = []
        
        print(f"Поиск в r/{subreddit_name}: '{query}'")
        print(f"Период: {time_filter}, Сортировка: {sort}")
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # Поиск постов
            search_results = subreddit.search(
                query=query,
                limit=limit,
                time_filter=time_filter,
                sort=sort
            )
            
            for post in search_results:
                # Собираем данные о посте
                post_info = {
                    'id': post.id,
                    'subreddit': str(post.subreddit),
                    'title': post.title,
                    'text': post.selftext,
                    'author': str(post.author) if post.author else '[deleted]',
                    'created_utc': datetime.fromtimestamp(post.created_utc),
                    'score': post.score,
                    'upvote_ratio': post.upvote_ratio,
                    'num_comments': post.num_comments,
                    'url': f"https://reddit.com{post.permalink}",
                    'is_self': post.is_self,
                    'link_flair_text': post.link_flair_text,
                    'engagement': post.score + post.num_comments,  # Простая метрика engagement
                }
                
                posts_data.append(post_info)
            
            print(f"✅ Найдено {len(posts_data)} постов в r/{subreddit_name}")
            
        except Exception as e:
            print(f"❌ Ошибка в r/{subreddit_name}: {e}")
            return pd.DataFrame()
        
        return pd.DataFrame(posts_data)
    
    def search_multiple_subreddits(self, subreddits, query, limit_per_subreddit=100, time_filter='month'):
        """
        Поиск по нескольким subreddits
        
        Args:
            subreddits: список названий subreddits
            query: поисковый запрос
            limit_per_subreddit: лимит постов на каждый subreddit
            time_filter: временной фильтр
        """
        all_posts = []
        
        for subreddit in subreddits:
            print(f"\n  Поиск в r/{subreddit}...")
            posts_df = self.search_subreddit(
                subreddit_name=subreddit,
                query=query,
                limit=limit_per_subreddit,
                time_filter=time_filter
            )
            
            if not posts_df.empty:
                all_posts.append(posts_df)
            
            # Задержка между запросами (rate limit)
            time.sleep(2)
        
        if not all_posts:
            return pd.DataFrame()
        
        combined = pd.concat(all_posts, ignore_index=True)
        
        # Удаляем дубликаты по ID
        combined = combined.drop_duplicates(subset=['id'])
        
        return combined
    
    def get_top_posts(self, subreddit_name, time_filter='month', limit=50):
        """
        Получить топовые посты из subreddit
        
        Полезно для понимания текущих трендов и проблем
        """
        posts_data = []
        
        print(f"Получение топ-постов из r/{subreddit_name} за {time_filter}")
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            for post in subreddit.top(time_filter=time_filter, limit=limit):
                post_info = {
                    'id': post.id,
                    'subreddit': str(post.subreddit),
                    'title': post.title,
                    'text': post.selftext,
                    'author': str(post.author) if post.author else '[deleted]',
                    'created_utc': datetime.fromtimestamp(post.created_utc),
                    'score': post.score,
                    'upvote_ratio': post.upvote_ratio,
                    'num_comments': post.num_comments,
                    'url': f"https://reddit.com{post.permalink}",
                    'engagement': post.score + post.num_comments,
                }
                
                posts_data.append(post_info)
            
            print(f"✅ Получено {len(posts_data)} топ-постов")
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return pd.DataFrame()
        
        return pd.DataFrame(posts_data)
    
    def find_pain_points(self, posts_df):
        """
        Анализ болевых точек в постах
        
        Ищет посты с маркерами проблем и фрустрации
        """
        if posts_df.empty:
            return pd.DataFrame()
        
        pain_keywords = [
            'struggling', 'frustrated', 'annoying', 'waste time', 'wasting time',
            'difficult', 'problem', 'issue', 'broken', 'hate', 'terrible',
            'wish', 'need', 'missing', 'slow', 'expensive', 'costly',
            'complicated', 'confusing', 'sucks', 'awful', 'pain',
            'nightmare', 'help', 'advice', 'how to', 'anyone know',
            'recommend', 'alternative', 'better than', 'tired of'
        ]
        
        pain_posts = []
        
        for _, post in posts_df.iterrows():
            # Проверяем title и text
            combined_text = f"{post['title']} {post['text']}".lower()
            
            matched_keywords = []
            for keyword in pain_keywords:
                if keyword in combined_text:
                    matched_keywords.append(keyword)
            
            if matched_keywords:
                pain_posts.append({
                    'post_id': post['id'],
                    'subreddit': post['subreddit'],
                    'title': post['title'],
                    'text': post['text'][:200] + '...' if len(post['text']) > 200 else post['text'],
                    'keywords': ', '.join(matched_keywords),
                    'engagement': post['engagement'],
                    'score': post['score'],
                    'num_comments': post['num_comments'],
                    'url': post['url']
                })
        
        return pd.DataFrame(pain_posts)
    
    def analyze_comments(self, post_id, limit=50):
        """
        Анализ комментариев к посту
        
        Комментарии часто содержат детальное описание проблем
        """
        comments_data = []
        
        try:
            submission = self.reddit.submission(id=post_id)
            submission.comments.replace_more(limit=0)  # Не загружаем "load more comments"
            
            for comment in submission.comments.list()[:limit]:
                if hasattr(comment, 'body'):
                    comments_data.append({
                        'comment_id': comment.id,
                        'author': str(comment.author) if comment.author else '[deleted]',
                        'text': comment.body,
                        'score': comment.score,
                        'created_utc': datetime.fromtimestamp(comment.created_utc),
                    })
            
        except Exception as e:
            print(f"❌ Ошибка при получении комментариев: {e}")
        
        return pd.DataFrame(comments_data)
    
    def get_subreddit_info(self, subreddit_name):
        """
        Получить информацию о subreddit
        
        Полезно для оценки размера аудитории
        """
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            info = {
                'name': subreddit.display_name,
                'title': subreddit.title,
                'description': subreddit.public_description,
                'subscribers': subreddit.subscribers,
                'active_users': subreddit.active_user_count,
                'created_utc': datetime.fromtimestamp(subreddit.created_utc),
                'url': f"https://reddit.com/r/{subreddit_name}"
            }
            
            return info
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return None
    
    def validate_saas_idea(self, idea_keywords, relevant_subreddits, output_file='reddit_validation.json'):
        """
        Полная валидация SaaS идеи через Reddit
        
        Args:
            idea_keywords: список ключевых слов, связанных с идеей
            relevant_subreddits: список релевантных subreddits
            output_file: файл для сохранения результатов
            
        Returns:
            dict с результатами валидации
        """
        print(f"\n{'='*60}")
        print(f"Reddit Валидация SaaS Идеи")
        print(f"{'='*60}\n")
        
        validation_results = {
            'analysis_date': datetime.now().isoformat(),
            'idea_keywords': idea_keywords,
            'subreddits_analyzed': relevant_subreddits,
            'subreddit_stats': [],
            'posts_found': 0,
            'pain_points_found': 0,
            'top_posts': [],
            'pain_point_posts': [],
            'common_issues': {},
            'potential_competitors': [],
            'market_size_estimate': 0
        }
        
        # 1. Анализ subreddits
        print("📊 Анализ subreddits:")
        for subreddit in relevant_subreddits:
            info = self.get_subreddit_info(subreddit)
            if info:
                validation_results['subreddit_stats'].append(info)
                validation_results['market_size_estimate'] += info['subscribers']
                print(f"  r/{subreddit}: {info['subscribers']:,} подписчиков, {info['active_users']:,} активных")
        
        # 2. Поиск постов по ключевым словам
        print("\n🔍 Поиск релевантных постов:")
        all_posts = []
        
        for keyword in idea_keywords:
            print(f"\n  Ключевое слово: '{keyword}'")
            posts = self.search_multiple_subreddits(
                subreddits=relevant_subreddits,
                query=keyword,
                limit_per_subreddit=50,
                time_filter='month'
            )
            if not posts.empty:
                all_posts.append(posts)
            time.sleep(1)
        
        if all_posts:
            combined_posts = pd.concat(all_posts, ignore_index=True)
            combined_posts = combined_posts.drop_duplicates(subset=['id'])
            validation_results['posts_found'] = len(combined_posts)
            
            # 3. Анализ болевых точек
            print("\n🔥 Анализ болевых точек:")
            pain_points = self.find_pain_points(combined_posts)
            validation_results['pain_points_found'] = len(pain_points)
            
            if not pain_points.empty:
                # Топ постов с болевыми точками
                top_pain = pain_points.nlargest(10, 'engagement')
                validation_results['pain_point_posts'] = top_pain.to_dict('records')
                
                # Анализ частых проблем
                all_keywords = []
                for keywords_str in pain_points['keywords']:
                    all_keywords.extend(keywords_str.split(', '))
                keyword_counter = Counter(all_keywords)
                validation_results['common_issues'] = dict(keyword_counter.most_common(20))
                
                print(f"  Найдено {len(pain_points)} постов с болевыми точками")
                print(f"\n  Топ проблем:")
                for issue, count in keyword_counter.most_common(10):
                    print(f"    '{issue}': {count} упоминаний")
            
            # 4. Топ посты по engagement
            top_posts = combined_posts.nlargest(10, 'engagement')
            validation_results['top_posts'] = top_posts[[
                'title', 'subreddit', 'score', 'num_comments', 'url'
            ]].to_dict('records')
            
            # 5. Оценка валидности идеи (scoring)
            score = 0
            reasons = []
            
            # Размер аудитории
            if validation_results['market_size_estimate'] > 100000:
                score += 25
                reasons.append("✅ Большая аудитория (100k+ подписчиков)")
            elif validation_results['market_size_estimate'] > 50000:
                score += 15
                reasons.append("✅ Средняя аудитория (50k+ подписчиков)")
            
            # Количество постов
            if validation_results['posts_found'] > 50:
                score += 20
                reasons.append("✅ Много релевантных постов (50+)")
            elif validation_results['posts_found'] > 20:
                score += 10
                reasons.append("✅ Есть релевантные посты (20+)")
            
            # Болевые точки
            if validation_results['pain_points_found'] > 20:
                score += 30
                reasons.append("✅ Много болевых точек (20+)")
            elif validation_results['pain_points_found'] > 10:
                score += 20
                reasons.append("✅ Есть болевые точки (10+)")
            elif validation_results['pain_points_found'] > 5:
                score += 10
                reasons.append("⚠️ Немного болевых точек (5+)")
            
            # Engagement
            avg_engagement = combined_posts['engagement'].mean()
            if avg_engagement > 100:
                score += 15
                reasons.append(f"✅ Высокий engagement (avg {avg_engagement:.0f})")
            elif avg_engagement > 50:
                score += 10
                reasons.append(f"✅ Средний engagement (avg {avg_engagement:.0f})")
            
            # Свежесть проблемы (посты за последний месяц)
            recent_posts = combined_posts[
                combined_posts['created_utc'] > datetime.now() - timedelta(days=30)
            ]
            if len(recent_posts) > 20:
                score += 10
                reasons.append("✅ Проблема актуальна (много свежих постов)")
            
            validation_results['validation_score'] = score
            validation_results['score_reasons'] = reasons
            
            # Интерпретация score
            if score >= 80:
                verdict = "🚀 ОТЛИЧНАЯ ИДЕЯ - Сильная валидация"
            elif score >= 60:
                verdict = "✅ ХОРОШАЯ ИДЕЯ - Есть потенциал"
            elif score >= 40:
                verdict = "⚠️ СРЕДНЯЯ ИДЕЯ - Нужны дополнительные исследования"
            else:
                verdict = "❌ СЛАБАЯ ВАЛИДАЦИЯ - Рекомендуется pivot"
            
            validation_results['verdict'] = verdict
            
        else:
            validation_results['verdict'] = "❌ НЕТ ДАННЫХ - Не найдено релевантных постов"
            validation_results['validation_score'] = 0
        
        # Сохранение результатов
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(validation_results, f, indent=2, ensure_ascii=False, default=str)
        
        # Вывод результатов
        print(f"\n{'='*60}")
        print(f"📊 РЕЗУЛЬТАТЫ ВАЛИДАЦИИ")
        print(f"{'='*60}")
        print(f"\n🎯 Оценка: {validation_results['validation_score']}/100")
        print(f"📋 Вердикт: {validation_results['verdict']}")
        print(f"\n📈 Статистика:")
        print(f"  - Размер аудитории: {validation_results['market_size_estimate']:,} подписчиков")
        print(f"  - Найдено постов: {validation_results['posts_found']}")
        print(f"  - Болевых точек: {validation_results['pain_points_found']}")
        
        if 'score_reasons' in validation_results:
            print(f"\n💡 Почему эта оценка:")
            for reason in validation_results['score_reasons']:
                print(f"  {reason}")
        
        print(f"\n✅ Полный отчет сохранен: {output_file}")
        
        return validation_results


class RedditAdvancedSearch:
    """
    Расширенные поисковые запросы и helper методы для Reddit
    """
    
    @staticmethod
    def get_saas_subreddits():
        """
        Список популярных subreddits для SaaS валидации
        """
        return {
            'general': ['SaaS', 'Entrepreneur', 'startups', 'smallbusiness'],
            'tech': ['webdev', 'programming', 'devops', 'sysadmin'],
            'marketing': ['marketing', 'digitalmarketing', 'SEO', 'PPC'],
            'productivity': ['productivity', 'gtd', 'organization'],
            'design': ['web_design', 'UI_Design', 'UXDesign'],
            'freelance': ['freelance', 'forhire', 'freelance_forhire']
        }
    
    @staticmethod
    def build_pain_query(topic):
        """
        Построить запрос для поиска болевых точек
        
        Reddit search поддерживает boolean операторы
        """
        pain_keywords = [
            'struggling', 'frustrated', 'problem', 'issue',
            'help', 'advice', 'how to', 'difficult'
        ]
        
        # Комбинируем topic с pain keywords
        queries = [f'"{topic}" "{keyword}"' for keyword in pain_keywords]
        
        return queries
    
    @staticmethod
    def build_solution_query(topic):
        """
        Построить запрос для поиска запросов на решение
        """
        solution_keywords = [
            'recommend', 'best tool', 'looking for',
            'need help', 'what do you use', 'alternative to'
        ]
        
        queries = [f'"{topic}" "{keyword}"' for keyword in solution_keywords]
        
        return queries
    
    @staticmethod
    def build_competitor_query(competitors):
        """
        Построить запрос для анализа конкурентов
        """
        queries = []
        for competitor in competitors:
            queries.append(f'"{competitor}"')
            queries.append(f'"{competitor}" alternative')
            queries.append(f'"{competitor}" vs')
        
        return queries


def main():
    """
    Пример использования Reddit scraper
    """
    
    # ВАЖНО: Замените на ваши credentials
    CLIENT_ID = "ваш_client_id"
    CLIENT_SECRET = "ваш_client_secret"
    USER_AGENT = "SaaS Validator 1.0 by u/yourname"
    
    scraper = RedditSaaSValidator(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent=USER_AGENT
    )
    
    # Пример 1: Простой поиск
    print("=" * 60)
    print("ПРИМЕР 1: Поиск в конкретном subreddit")
    print("=" * 60)
    
    posts = scraper.search_subreddit(
        subreddit_name='SaaS',
        query='email marketing',
        limit=50,
        time_filter='month'
    )
    
    if not posts.empty:
        posts.to_csv('reddit_posts.csv', index=False, encoding='utf-8')
        print(f"\n✅ Сохранено в reddit_posts.csv")
    
    # Пример 2: Поиск по нескольким subreddits
    print("\n" + "=" * 60)
    print("ПРИМЕР 2: Поиск по нескольким subreddits")
    print("=" * 60)
    
    subreddits = ['SaaS', 'Entrepreneur', 'startups', 'smallbusiness']
    
    all_posts = scraper.search_multiple_subreddits(
        subreddits=subreddits,
        query='cold email',
        limit_per_subreddit=30,
        time_filter='month'
    )
    
    if not all_posts.empty:
        # Анализ болевых точек
        pain_points = scraper.find_pain_points(all_posts)
        
        if not pain_points.empty:
            pain_points.to_csv('reddit_pain_points.csv', index=False)
            print(f"\n✅ Найдено {len(pain_points)} постов с болевыми точками")
    
    # Пример 3: Полная валидация идеи
    print("\n" + "=" * 60)
    print("ПРИМЕР 3: Полная валидация SaaS идеи")
    print("=" * 60)
    
    idea_keywords = [
        'email automation',
        'cold email tool',
        'email outreach',
        'email marketing software'
    ]
    
    relevant_subreddits = ['SaaS', 'Entrepreneur', 'marketing', 'sales']
    
    validation = scraper.validate_saas_idea(
        idea_keywords=idea_keywords,
        relevant_subreddits=relevant_subreddits,
        output_file='reddit_validation.json'
    )
    
    # Пример 4: Анализ топ-постов для понимания трендов
    print("\n" + "=" * 60)
    print("ПРИМЕР 4: Анализ топ-постов")
    print("=" * 60)
    
    top_posts = scraper.get_top_posts(
        subreddit_name='SaaS',
        time_filter='month',
        limit=20
    )
    
    if not top_posts.empty:
        print("\nТоп-5 постов за месяц:")
        for _, post in top_posts.head(5).iterrows():
            print(f"\n  📌 {post['title']}")
            print(f"     ⬆️ {post['score']} | 💬 {post['num_comments']} | 🔗 {post['url']}")
    
    # Пример 5: Анализ конкурентов
    print("\n" + "=" * 60)
    print("ПРИМЕР 5: Анализ упоминаний конкурентов")
    print("=" * 60)
    
    competitors = ['mailchimp', 'sendgrid', 'convertkit']
    competitor_queries = RedditAdvancedSearch.build_competitor_query(competitors)
    
    for query in competitor_queries[:3]:  # Первые 3 запроса
        print(f"\nЗапрос: {query}")
        posts = scraper.search_subreddit(
            subreddit_name='marketing',
            query=query,
            limit=20,
            time_filter='month'
        )
        
        if not posts.empty:
            print(f"  Найдено {len(posts)} постов")


if __name__ == "__main__":
    main()
