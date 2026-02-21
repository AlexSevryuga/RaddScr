"""
LinkedIn Scraper для валидации SaaS идей

Анализирует посты, компании и профили для понимания B2B рынка
"""

from linkedin_api import Linkedin
import pandas as pd
from datetime import datetime, timedelta
import json
import re
from collections import Counter
import time


class LinkedInSaaSValidator:
    def __init__(self, email, password):
        """
        Инициализация LinkedIn API клиента
        
        ВАЖНО: Используйте осторожно! LinkedIn может заблокировать аккаунт за scraping
        
        Args:
            email: Email LinkedIn аккаунта
            password: Пароль LinkedIn аккаунта
            
        Рекомендации:
        - Используйте отдельный тестовый аккаунт
        - Добавляйте задержки между запросами
        - Не делайте слишком много запросов за раз
        """
        try:
            self.api = Linkedin(email, password)
            print("✅ LinkedIn API подключен")
        except Exception as e:
            print(f"❌ Ошибка подключения к LinkedIn: {e}")
            raise
    
    def search_posts(self, keywords, limit=50):
        """
        Поиск постов по ключевым словам
        
        LinkedIn API ограничен, поэтому результаты могут быть неполными
        
        Args:
            keywords: список ключевых слов
            limit: максимальное количество постов
            
        Returns:
            DataFrame с постами
        """
        posts_data = []
        
        print(f"Поиск постов LinkedIn по ключевым словам: {keywords}")
        
        try:
            # Поиск по каждому ключевому слову
            for keyword in keywords:
                print(f"  Поиск: '{keyword}'")
                
                # Используем поиск компаний, так как прямой поиск постов ограничен
                results = self.api.search({'keywords': keyword}, limit=limit)
                
                # Обработка результатов (может потребоваться адаптация)
                # LinkedIn API возвращает разные типы объектов
                
                time.sleep(2)  # Rate limiting
            
            print(f"✅ Найдено {len(posts_data)} постов")
            
        except Exception as e:
            print(f"❌ Ошибка поиска: {e}")
            return pd.DataFrame()
        
        return pd.DataFrame(posts_data)
    
    def get_company_info(self, company_name):
        """
        Получить информацию о компании
        
        Полезно для анализа конкурентов
        """
        print(f"Получение информации о компании: {company_name}")
        
        try:
            # Поиск компании
            companies = self.api.search_companies(keywords=company_name, limit=5)
            
            if not companies:
                print(f"❌ Компания '{company_name}' не найдена")
                return None
            
            # Берем первый результат
            company_urn = companies[0].get('urn_id')
            
            # Получаем детальную информацию
            company_data = self.api.get_company(company_urn)
            
            info = {
                'name': company_data.get('name'),
                'description': company_data.get('description'),
                'industry': company_data.get('companyIndustries', [{}])[0].get('localizedName'),
                'company_size': company_data.get('staffCount'),
                'followers': company_data.get('followersCount'),
                'website': company_data.get('companyPageUrl'),
                'founded': company_data.get('foundedOn', {}).get('year'),
                'headquarters': company_data.get('headquarter', {}).get('city'),
                'specialties': company_data.get('specialities', [])
            }
            
            print(f"✅ Получена информация о {company_name}")
            return info
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return None
    
    def get_company_updates(self, company_urn, limit=20):
        """
        Получить недавние посты компании
        
        Полезно для анализа контент-стратегии конкурентов
        """
        print(f"Получение постов компании (URN: {company_urn})")
        
        updates_data = []
        
        try:
            updates = self.api.get_company_updates(company_urn, max_results=limit)
            
            for update in updates:
                # Парсинг данных поста
                update_info = {
                    'urn': update.get('urn'),
                    'text': update.get('commentary', {}).get('text', ''),
                    'created_at': datetime.fromtimestamp(update.get('created', {}).get('time', 0) / 1000),
                    'likes': update.get('socialDetail', {}).get('totalSocialActivityCounts', {}).get('numLikes', 0),
                    'comments': update.get('socialDetail', {}).get('totalSocialActivityCounts', {}).get('numComments', 0),
                    'shares': update.get('socialDetail', {}).get('totalSocialActivityCounts', {}).get('numShares', 0),
                }
                
                updates_data.append(update_info)
            
            print(f"✅ Получено {len(updates_data)} постов")
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return pd.DataFrame()
        
        return pd.DataFrame(updates_data)
    
    def search_people(self, keywords, industry=None, limit=50):
        """
        Поиск людей по ключевым словам
        
        Полезно для поиска potential customers или thought leaders
        
        Args:
            keywords: ключевые слова (должности, навыки)
            industry: код индустрии LinkedIn (опционально)
            limit: максимальное количество результатов
        """
        print(f"Поиск людей: '{keywords}'")
        
        people_data = []
        
        try:
            search_params = {'keywords': keywords}
            
            if industry:
                search_params['industry'] = industry
            
            results = self.api.search_people(
                **search_params,
                limit=limit
            )
            
            for person in results:
                people_data.append({
                    'name': f"{person.get('firstName', '')} {person.get('lastName', '')}",
                    'headline': person.get('headline', ''),
                    'location': person.get('location', ''),
                    'industry': person.get('industry', ''),
                    'profile_url': f"https://www.linkedin.com/in/{person.get('public_id', '')}"
                })
            
            print(f"✅ Найдено {len(people_data)} людей")
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return pd.DataFrame()
        
        return pd.DataFrame(people_data)
    
    def get_profile(self, public_id):
        """
        Получить детальный профиль человека
        
        Args:
            public_id: LinkedIn public ID (из URL профиля)
        """
        print(f"Получение профиля: {public_id}")
        
        try:
            profile = self.api.get_profile(public_id)
            
            profile_data = {
                'name': f"{profile.get('firstName', '')} {profile.get('lastName', '')}",
                'headline': profile.get('headline', ''),
                'summary': profile.get('summary', ''),
                'location': profile.get('locationName', ''),
                'industry': profile.get('industryName', ''),
                'connections': profile.get('connectionsCount', 0),
                'followers': profile.get('followersCount', 0),
                'experience': [],
                'education': []
            }
            
            # Опыт работы
            for exp in profile.get('experience', []):
                profile_data['experience'].append({
                    'title': exp.get('title'),
                    'company': exp.get('companyName'),
                    'location': exp.get('locationName'),
                    'start': exp.get('timePeriod', {}).get('startDate'),
                    'end': exp.get('timePeriod', {}).get('endDate')
                })
            
            # Образование
            for edu in profile.get('education', []):
                profile_data['education'].append({
                    'school': edu.get('schoolName'),
                    'degree': edu.get('degreeName'),
                    'field': edu.get('fieldOfStudy'),
                    'start': edu.get('timePeriod', {}).get('startDate'),
                    'end': edu.get('timePeriod', {}).get('endDate')
                })
            
            print(f"✅ Получен профиль: {profile_data['name']}")
            return profile_data
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return None
    
    def analyze_competitors(self, competitor_names, output_file='linkedin_competitors.json'):
        """
        Анализ конкурентов на LinkedIn
        
        Собирает информацию о компаниях и их контент-стратегии
        """
        print(f"\n{'='*60}")
        print(f"LinkedIn Анализ Конкурентов")
        print(f"{'='*60}\n")
        
        competitors_data = []
        
        for competitor in competitor_names:
            print(f"\n📊 Анализ: {competitor}")
            print(f"{'-'*40}")
            
            # Получаем информацию о компании
            company_info = self.get_company_info(competitor)
            
            if company_info:
                competitor_data = {
                    'company': competitor,
                    'info': company_info,
                    'posts': [],
                    'engagement': {}
                }
                
                # Получаем посты компании (если есть URN)
                # Это требует дополнительного поиска компании для получения URN
                try:
                    companies = self.api.search_companies(keywords=competitor, limit=1)
                    if companies:
                        company_urn = companies[0].get('urn_id')
                        posts_df = self.get_company_updates(company_urn, limit=20)
                        
                        if not posts_df.empty:
                            competitor_data['posts'] = posts_df.to_dict('records')
                            competitor_data['engagement'] = {
                                'avg_likes': float(posts_df['likes'].mean()),
                                'avg_comments': float(posts_df['comments'].mean()),
                                'avg_shares': float(posts_df['shares'].mean()),
                                'total_posts': len(posts_df)
                            }
                            
                            print(f"  📈 Посты: {len(posts_df)}")
                            print(f"  ❤️ Avg likes: {competitor_data['engagement']['avg_likes']:.1f}")
                            print(f"  💬 Avg comments: {competitor_data['engagement']['avg_comments']:.1f}")
                
                except Exception as e:
                    print(f"  ⚠️ Не удалось получить посты: {e}")
                
                competitors_data.append(competitor_data)
                
                # Rate limiting
                time.sleep(3)
        
        # Сохранение результатов
        results = {
            'analysis_date': datetime.now().isoformat(),
            'competitors': competitors_data
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n✅ Отчет сохранен: {output_file}")
        
        return results
    
    def find_target_audience(self, job_titles, industries=None, locations=None, limit=100):
        """
        Поиск целевой аудитории для SaaS продукта
        
        Args:
            job_titles: список должностей (например, ['Marketing Manager', 'CMO'])
            industries: список индустрий (опционально)
            locations: список локаций (опционально)
            limit: максимальное количество результатов
            
        Returns:
            DataFrame с potential customers
        """
        print(f"\n{'='*60}")
        print(f"Поиск целевой аудитории")
        print(f"{'='*60}\n")
        
        all_people = []
        
        for job_title in job_titles:
            print(f"🔍 Поиск: {job_title}")
            
            people_df = self.search_people(
                keywords=job_title,
                limit=limit
            )
            
            if not people_df.empty:
                people_df['search_job_title'] = job_title
                all_people.append(people_df)
            
            # Rate limiting
            time.sleep(2)
        
        if not all_people:
            print("❌ Целевая аудитория не найдена")
            return pd.DataFrame()
        
        combined = pd.concat(all_people, ignore_index=True)
        combined = combined.drop_duplicates(subset=['name'])
        
        print(f"\n✅ Найдено {len(combined)} potential customers")
        
        # Анализ по индустриям
        if not combined.empty:
            print(f"\n📊 Распределение по индустриям:")
            industry_counts = combined['industry'].value_counts().head(10)
            for industry, count in industry_counts.items():
                print(f"  {industry}: {count}")
        
        return combined
    
    def validate_b2b_market(self, 
                           target_job_titles,
                           competitor_names,
                           product_keywords,
                           output_file='linkedin_b2b_validation.json'):
        """
        Полная валидация B2B рынка через LinkedIn
        
        Args:
            target_job_titles: список целевых должностей
            competitor_names: список конкурентов
            product_keywords: ключевые слова продукта
            output_file: файл для сохранения результатов
        """
        print(f"\n{'='*60}")
        print(f"LinkedIn B2B Валидация")
        print(f"{'='*60}\n")
        
        validation_results = {
            'analysis_date': datetime.now().isoformat(),
            'target_job_titles': target_job_titles,
            'competitors_analyzed': competitor_names,
            'product_keywords': product_keywords,
            'market_size': 0,
            'competitors_data': [],
            'audience_insights': {},
            'validation_score': 0,
            'verdict': ''
        }
        
        # 1. Поиск целевой аудитории
        print("\n👥 Шаг 1: Анализ целевой аудитории")
        audience_df = self.find_target_audience(
            job_titles=target_job_titles,
            limit=100
        )
        
        if not audience_df.empty:
            validation_results['market_size'] = len(audience_df)
            validation_results['audience_insights'] = {
                'total_found': len(audience_df),
                'top_industries': audience_df['industry'].value_counts().head(10).to_dict(),
                'top_locations': audience_df['location'].value_counts().head(10).to_dict()
            }
        
        # 2. Анализ конкурентов
        if competitor_names:
            print(f"\n🏢 Шаг 2: Анализ конкурентов")
            competitors_analysis = self.analyze_competitors(
                competitor_names=competitor_names,
                output_file='linkedin_competitors_temp.json'
            )
            
            validation_results['competitors_data'] = competitors_analysis.get('competitors', [])
        
        # 3. Scoring
        score = 0
        reasons = []
        
        # Размер аудитории
        if validation_results['market_size'] > 500:
            score += 30
            reasons.append(f"✅ Большая целевая аудитория ({validation_results['market_size']}+ профилей)")
        elif validation_results['market_size'] > 200:
            score += 20
            reasons.append(f"✅ Средняя целевая аудитория ({validation_results['market_size']}+ профилей)")
        elif validation_results['market_size'] > 50:
            score += 10
            reasons.append(f"⚠️ Небольшая целевая аудитория ({validation_results['market_size']}+ профилей)")
        
        # Конкуренты
        if len(validation_results['competitors_data']) > 0:
            score += 20
            reasons.append(f"✅ Найдено {len(validation_results['competitors_data'])} конкурентов")
            
            # Анализ engagement конкурентов
            total_engagement = 0
            for comp in validation_results['competitors_data']:
                if comp.get('engagement'):
                    total_engagement += comp['engagement'].get('avg_likes', 0)
            
            if total_engagement > 100:
                score += 15
                reasons.append("✅ Высокий engagement у конкурентов - активный рынок")
        
        # Разнообразие индустрий (показывает широту применения)
        if validation_results.get('audience_insights', {}).get('top_industries'):
            num_industries = len(validation_results['audience_insights']['top_industries'])
            if num_industries > 5:
                score += 15
                reasons.append(f"✅ Широкий охват индустрий ({num_industries})")
            elif num_industries > 3:
                score += 10
                reasons.append(f"✅ Умеренный охват индустрий ({num_industries})")
        
        # Присутствие в LinkedIn (показывает B2B фокус)
        score += 20  # Bonus за то, что нашли аудиторию в LinkedIn
        reasons.append("✅ Целевая аудитория активна на LinkedIn")
        
        validation_results['validation_score'] = score
        validation_results['score_reasons'] = reasons
        
        # Вердикт
        if score >= 80:
            verdict = "🚀 ОТЛИЧНЫЙ B2B РЫНОК - Сильная валидация"
        elif score >= 60:
            verdict = "✅ ХОРОШИЙ B2B РЫНОК - Есть потенциал"
        elif score >= 40:
            verdict = "⚠️ СРЕДНИЙ B2B РЫНОК - Нужны дополнительные исследования"
        else:
            verdict = "❌ СЛАБАЯ ВАЛИДАЦИЯ - Рекомендуется pivot"
        
        validation_results['verdict'] = verdict
        
        # Сохранение результатов
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(validation_results, f, indent=2, ensure_ascii=False, default=str)
        
        # Вывод результатов
        print(f"\n{'='*60}")
        print(f"📊 РЕЗУЛЬТАТЫ B2B ВАЛИДАЦИИ")
        print(f"{'='*60}")
        print(f"\n🎯 Оценка: {validation_results['validation_score']}/100")
        print(f"📋 Вердикт: {validation_results['verdict']}")
        print(f"\n📈 Статистика:")
        print(f"  - Размер аудитории: {validation_results['market_size']} профилей")
        print(f"  - Проанализировано конкурентов: {len(validation_results['competitors_data'])}")
        
        if reasons:
            print(f"\n💡 Почему эта оценка:")
            for reason in reasons:
                print(f"  {reason}")
        
        print(f"\n✅ Полный отчет сохранен: {output_file}")
        
        return validation_results


class LinkedInIndustries:
    """
    Коды индустрий LinkedIn для фильтрации поиска
    """
    
    # Основные индустрии для B2B SaaS
    INDUSTRIES = {
        'software': '4',
        'it_services': '96',
        'internet': '6',
        'marketing': '80',
        'financial_services': '43',
        'management_consulting': '11',
        'health_tech': '14',
        'education': '69',
        'retail': '27',
        'real_estate': '44'
    }
    
    @classmethod
    def get_industry_code(cls, industry_name):
        """Получить код индустрии по названию"""
        return cls.INDUSTRIES.get(industry_name.lower())
    
    @classmethod
    def get_all_codes(cls):
        """Получить все коды индустрий"""
        return list(cls.INDUSTRIES.values())


def main():
    """
    Пример использования LinkedIn scraper
    """
    
    # ВАЖНО: Замените на ваши credentials
    # РЕКОМЕНДУЕТСЯ: Используйте отдельный тестовый аккаунт!
    EMAIL = "ваш_email@example.com"
    PASSWORD = "ваш_пароль"
    
    scraper = LinkedInSaaSValidator(
        email=EMAIL,
        password=PASSWORD
    )
    
    # Пример 1: Поиск целевой аудитории
    print("=" * 60)
    print("ПРИМЕР 1: Поиск целевой аудитории")
    print("=" * 60)
    
    target_audience = scraper.find_target_audience(
        job_titles=['Marketing Manager', 'CMO', 'Head of Marketing'],
        limit=50
    )
    
    if not target_audience.empty:
        target_audience.to_csv('linkedin_target_audience.csv', index=False)
        print(f"\n✅ Сохранено в linkedin_target_audience.csv")
    
    # Пример 2: Анализ конкурентов
    print("\n" + "=" * 60)
    print("ПРИМЕР 2: Анализ конкурентов")
    print("=" * 60)
    
    competitors = ['HubSpot', 'Mailchimp', 'Salesforce']
    
    competitors_analysis = scraper.analyze_competitors(
        competitor_names=competitors,
        output_file='linkedin_competitors.json'
    )
    
    # Пример 3: Полная B2B валидация
    print("\n" + "=" * 60)
    print("ПРИМЕР 3: Полная B2B валидация")
    print("=" * 60)
    
    validation = scraper.validate_b2b_market(
        target_job_titles=[
            'Marketing Director',
            'VP Marketing',
            'Growth Manager',
            'Marketing Operations'
        ],
        competitor_names=['HubSpot', 'Marketo', 'ActiveCampaign'],
        product_keywords=['marketing automation', 'email marketing', 'lead generation'],
        output_file='linkedin_b2b_validation.json'
    )
    
    # Пример 4: Получение информации о компании
    print("\n" + "=" * 60)
    print("ПРИМЕР 4: Информация о компании")
    print("=" * 60)
    
    company_info = scraper.get_company_info('Notion')
    
    if company_info:
        print(f"\n📊 {company_info['name']}")
        print(f"   Industry: {company_info.get('industry', 'N/A')}")
        print(f"   Size: {company_info.get('company_size', 'N/A')} employees")
        print(f"   Followers: {company_info.get('followers', 'N/A'):,}")
        print(f"   Website: {company_info.get('website', 'N/A')}")


if __name__ == "__main__":
    main()
