"""
🚀 МУЛЬТИПЛАТФОРМЕННЫЙ ВАЛИДАТОР SaaS ИДЕЙ

Объединяет данные из Reddit, Twitter/X и LinkedIn для комплексной валидации
"""

from .reddit_scraper import RedditSaaSValidator
from .twitter_scraper import TwitterSaaSValidator, TwitterAdvancedSearch
from .linkedin_scraper import LinkedInSaaSValidator
import pandas as pd
import json
from datetime import datetime
from collections import Counter
import os


class MultiPlatformValidator:
    """
    Объединенный анализ из нескольких платформ
    """
    
    def __init__(self, reddit_creds=None, twitter_creds=None, linkedin_creds=None):
        """
        Инициализация всех доступных платформ
        
        Args:
            reddit_creds: dict {'client_id': '', 'client_secret': '', 'user_agent': ''}
            twitter_creds: dict {'bearer_token': ''}
            linkedin_creds: dict {'email': '', 'password': ''}
        """
        self.platforms = {}
        
        # Инициализация Reddit
        if reddit_creds:
            try:
                self.platforms['reddit'] = RedditSaaSValidator(
                    client_id=reddit_creds['client_id'],
                    client_secret=reddit_creds['client_secret'],
                    user_agent=reddit_creds['user_agent']
                )
                print("✅ Reddit подключен")
            except Exception as e:
                print(f"⚠️ Reddit не подключен: {e}")
        
        # Инициализация Twitter
        if twitter_creds:
            try:
                self.platforms['twitter'] = TwitterSaaSValidator(
                    bearer_token=twitter_creds['bearer_token']
                )
                print("✅ Twitter/X подключен")
            except Exception as e:
                print(f"⚠️ Twitter не подключен: {e}")
        
        # Инициализация LinkedIn
        if linkedin_creds:
            try:
                self.platforms['linkedin'] = LinkedInSaaSValidator(
                    email=linkedin_creds['email'],
                    password=linkedin_creds['password']
                )
                print("✅ LinkedIn подключен")
            except Exception as e:
                print(f"⚠️ LinkedIn не подключен: {e}")
    
    def validate_idea(self, idea_name, keywords, subreddits=None, 
                     target_job_titles=None, competitor_names=None,
                     output_dir='validation_results'):
        """
        Полная валидация идеи через все доступные платформы
        
        Args:
            idea_name: название вашей идеи
            keywords: список ключевых слов для поиска
            subreddits: список subreddit'ов для Reddit
            target_job_titles: список целевых должностей для LinkedIn
            competitor_names: список конкурентов
            output_dir: директория для сохранения результатов
            
        Returns:
            dict с результатами валидации
        """
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"\n{'='*70}")
        print(f"🎯 МУЛЬТИПЛАТФОРМЕННАЯ ВАЛИДАЦИЯ: {idea_name}")
        print(f"{'='*70}\n")
        
        results = {
            'idea_name': idea_name,
            'analysis_date': datetime.now().isoformat(),
            'keywords': keywords,
            'platforms_analyzed': [],
            'reddit_data': {},
            'twitter_data': {},
            'linkedin_data': {},
            'overall_score': 0,
            'verdict': '',
            'key_insights': [],
            'recommendations': []
        }
        
        platform_scores = {}
        
        # ============ REDDIT АНАЛИЗ ============
        if 'reddit' in self.platforms and subreddits:
            print("\n📱 REDDIT АНАЛИЗ")
            print("-" * 70)
            
            try:
                reddit_validation = self.platforms['reddit'].validate_saas_idea(
                    idea_keywords=keywords,
                    relevant_subreddits=subreddits,
                    output_file=f'{output_dir}/reddit_validation.json'
                )
                
                results['platforms_analyzed'].append('reddit')
                results['reddit_data'] = {
                    'posts_found': reddit_validation.get('posts_found', 0),
                    'pain_points': reddit_validation.get('pain_points_found', 0),
                    'market_size': reddit_validation.get('market_size_estimate', 0),
                    'score': reddit_validation.get('validation_score', 0),
                    'verdict': reddit_validation.get('verdict', '')
                }
                
                platform_scores['reddit'] = reddit_validation.get('validation_score', 0)
                
                print(f"  ✅ Reddit: {results['reddit_data']['posts_found']} постов, "
                      f"{results['reddit_data']['pain_points']} pain points")
                print(f"  📊 Оценка: {results['reddit_data']['score']}/100")
                
            except Exception as e:
                print(f"  ❌ Ошибка Reddit: {e}")
        
        # ============ TWITTER АНАЛИЗ ============
        if 'twitter' in self.platforms:
            print("\n🐦 TWITTER/X АНАЛИЗ")
            print("-" * 70)
            
            try:
                twitter_report, twitter_df = self.platforms['twitter'].generate_report(
                    keywords=keywords,
                    output_file=f'{output_dir}/twitter_analysis.json'
                )
                
                if twitter_report:
                    results['platforms_analyzed'].append('twitter')
                    results['twitter_data'] = {
                        'tweets_found': twitter_report.get('total_tweets', 0),
                        'pain_points': twitter_report.get('pain_points_count', 0),
                        'avg_engagement': twitter_report.get('engagement_stats', {}).get('avg_likes', 0),
                        'total_engagement': twitter_report.get('engagement_stats', {}).get('total_engagement', 0),
                        'top_hashtags': list(twitter_report.get('top_hashtags', {}).keys())[:5]
                    }
                    
                    # Scoring для Twitter (0-100)
                    twitter_score = 0
                    if results['twitter_data']['tweets_found'] > 50:
                        twitter_score += 30
                    elif results['twitter_data']['tweets_found'] > 20:
                        twitter_score += 20
                    
                    if results['twitter_data']['pain_points'] > 10:
                        twitter_score += 30
                    elif results['twitter_data']['pain_points'] > 5:
                        twitter_score += 20
                    
                    if results['twitter_data']['avg_engagement'] > 50:
                        twitter_score += 20
                    elif results['twitter_data']['avg_engagement'] > 20:
                        twitter_score += 10
                    
                    if results['twitter_data']['total_engagement'] > 1000:
                        twitter_score += 20
                    elif results['twitter_data']['total_engagement'] > 500:
                        twitter_score += 10
                    
                    platform_scores['twitter'] = twitter_score
                    results['twitter_data']['score'] = twitter_score
                    
                    print(f"  ✅ Twitter: {results['twitter_data']['tweets_found']} твитов, "
                          f"{results['twitter_data']['pain_points']} pain points")
                    print(f"  📊 Оценка: {twitter_score}/100")
                
            except Exception as e:
                print(f"  ❌ Ошибка Twitter: {e}")
        
        # ============ LINKEDIN АНАЛИЗ ============
        if 'linkedin' in self.platforms and target_job_titles:
            print("\n💼 LINKEDIN АНАЛИЗ")
            print("-" * 70)
            
            try:
                linkedin_validation = self.platforms['linkedin'].validate_b2b_market(
                    target_job_titles=target_job_titles,
                    competitor_names=competitor_names or [],
                    product_keywords=keywords,
                    output_file=f'{output_dir}/linkedin_b2b_validation.json'
                )
                
                results['platforms_analyzed'].append('linkedin')
                results['linkedin_data'] = {
                    'market_size': linkedin_validation.get('market_size', 0),
                    'competitors': len(linkedin_validation.get('competitors_data', [])),
                    'score': linkedin_validation.get('validation_score', 0),
                    'verdict': linkedin_validation.get('verdict', '')
                }
                
                platform_scores['linkedin'] = linkedin_validation.get('validation_score', 0)
                
                print(f"  ✅ LinkedIn: {results['linkedin_data']['market_size']} профилей, "
                      f"{results['linkedin_data']['competitors']} конкурентов")
                print(f"  📊 Оценка: {results['linkedin_data']['score']}/100")
                
            except Exception as e:
                print(f"  ❌ Ошибка LinkedIn: {e}")
        
        # ============ ОБЩАЯ ОЦЕНКА ============
        if platform_scores:
            # Средневзвешенная оценка
            results['overall_score'] = int(sum(platform_scores.values()) / len(platform_scores))
            
            # Генерация инсайтов
            results['key_insights'] = self._generate_insights(results)
            
            # Генерация рекомендаций
            results['recommendations'] = self._generate_recommendations(results)
            
            # Вердикт
            score = results['overall_score']
            if score >= 80:
                results['verdict'] = "🚀 ОТЛИЧНАЯ ИДЕЯ - Сильная валидация"
            elif score >= 60:
                results['verdict'] = "✅ ХОРОШАЯ ИДЕЯ - Есть потенциал"
            elif score >= 40:
                results['verdict'] = "⚠️ СРЕДНЯЯ ИДЕЯ - Нужны дополнительные исследования"
            else:
                results['verdict'] = "❌ СЛАБАЯ ВАЛИДАЦИЯ - Рекомендуется pivot"
            
            print(f"\n{'='*70}")
            print(f"📊 ОБЩАЯ ОЦЕНКА: {results['overall_score']}/100")
            print(f"📋 {results['verdict']}")
            print(f"{'='*70}\n")
            
            # Сохранение общего отчёта
            with open(f'{output_dir}/multiplatform_report.json', 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)
            
            return results
        else:
            print("\n❌ Не удалось собрать данные ни с одной платформы")
            results['verdict'] = "❌ НЕТ ДАННЫХ"
            return results
    
    def _generate_insights(self, results):
        """Генерирует ключевые инсайты на основе результатов"""
        insights = []
        
        # Reddit инсайты
        if 'reddit' in results['platforms_analyzed']:
            reddit_data = results['reddit_data']
            if reddit_data.get('pain_points', 0) > 20:
                insights.append(f"На Reddit найдено {reddit_data['pain_points']} болевых точек - проблема реальна")
            if reddit_data.get('market_size', 0) > 100000:
                insights.append(f"Большая аудитория на Reddit ({reddit_data['market_size']:,} подписчиков)")
        
        # Twitter инсайты
        if 'twitter' in results['platforms_analyzed']:
            twitter_data = results['twitter_data']
            if twitter_data.get('total_engagement', 0) > 1000:
                insights.append(f"Высокий engagement на Twitter ({twitter_data['total_engagement']:,}) - тема популярна")
            if twitter_data.get('top_hashtags'):
                top_hashtag = twitter_data['top_hashtags'][0]
                insights.append(f"Популярный хештег: #{top_hashtag}")
        
        # LinkedIn инсайты
        if 'linkedin' in results['platforms_analyzed']:
            linkedin_data = results['linkedin_data']
            if linkedin_data.get('market_size', 0) > 500:
                insights.append(f"Большая B2B аудитория на LinkedIn ({linkedin_data['market_size']}+ профилей)")
            if linkedin_data.get('competitors', 0) > 0:
                insights.append(f"Найдено {linkedin_data['competitors']} конкурентов - рынок существует")
        
        # Общие инсайты
        if results['overall_score'] >= 70:
            insights.append("Идея показывает сильные сигналы валидации на нескольких платформах")
        
        return insights[:10]  # Макс 10 инсайтов
    
    def _generate_recommendations(self, results):
        """Генерирует рекомендации на основе результатов"""
        recommendations = []
        score = results['overall_score']
        
        if score >= 80:
            recommendations.append("Начните разработку MVP как можно скорее")
            recommendations.append("Создайте landing page и соберите email-подписки")
            recommendations.append("Проведите интервью с 10-20 potential customers")
        elif score >= 60:
            recommendations.append("Углубите исследование конкретных pain points")
            recommendations.append("Проанализируйте конкурентов детально")
            recommendations.append("Создайте простой landing page для сбора интереса")
        elif score >= 40:
            recommendations.append("Проведите дополнительные customer interviews")
            recommendations.append("Уточните целевую аудиторию")
            recommendations.append("Рассмотрите сужение или расширение scope")
        else:
            recommendations.append("Рассмотрите pivot - валидация слабая")
            recommendations.append("Изучите другие проблемы в этой сфере")
            recommendations.append("Проведите более глубокое customer research")
        
        # Специфичные рекомендации по платформам
        if 'reddit' in results['platforms_analyzed']:
            if results['reddit_data'].get('pain_points', 0) > 10:
                recommendations.append("Контактируйте с авторами постов с pain points на Reddit")
        
        if 'twitter' in results['platforms_analyzed']:
            if results['twitter_data'].get('top_hashtags'):
                recommendations.append(f"Используйте хештеги для продвижения: {', '.join(f'#{h}' for h in results['twitter_data']['top_hashtags'][:3])}")
        
        if 'linkedin' in results['platforms_analyzed']:
            if results['linkedin_data'].get('market_size', 0) > 100:
                recommendations.append("Начните outreach на LinkedIn к целевой аудитории")
        
        return recommendations[:10]  # Макс 10 рекомендаций


def main():
    """
    Пример использования мультиплатформенного валидатора
    """
    import os
    from dotenv import load_dotenv
    
    # Загрузка credentials
    load_dotenv()
    
    # Reddit credentials
    reddit_creds = {
        'client_id': os.getenv('REDDIT_CLIENT_ID'),
        'client_secret': os.getenv('REDDIT_CLIENT_SECRET'),
        'user_agent': os.getenv('REDDIT_USER_AGENT')
    }
    
    # Twitter credentials
    twitter_creds = {
        'bearer_token': os.getenv('TWITTER_BEARER_TOKEN')
    }
    
    # LinkedIn credentials
    linkedin_creds = {
        'email': os.getenv('LINKEDIN_EMAIL'),
        'password': os.getenv('LINKEDIN_PASSWORD')
    }
    
    # Инициализация валидатора
    validator = MultiPlatformValidator(
        reddit_creds=reddit_creds if reddit_creds['client_id'] else None,
        twitter_creds=twitter_creds if twitter_creds['bearer_token'] else None,
        linkedin_creds=linkedin_creds if linkedin_creds['email'] else None
    )
    
    # Пример: Валидация идеи "email marketing automation"
    print("\n" + "="*70)
    print("ПРИМЕР: Валидация идеи 'Email Marketing Automation'")
    print("="*70)
    
    results = validator.validate_idea(
        idea_name="Email Marketing Automation",
        keywords=[
            'email marketing',
            'email automation',
            'cold email',
            'email campaign',
            'newsletter tool'
        ],
        subreddits=['marketing', 'SaaS', 'Entrepreneur', 'sales'],
        target_job_titles=['Marketing Manager', 'CMO', 'Growth Manager'],
        competitor_names=['Mailchimp', 'SendGrid', 'ConvertKit']
    )
    
    print(f"\n✅ Анализ завершён!")
    print(f"📄 Результаты сохранены в: validation_results/")


if __name__ == "__main__":
    main()
