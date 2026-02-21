#!/usr/bin/env python3
"""
Reddit SaaS Validator - CLI Interface
Валидация SaaS идей через анализ Reddit, Twitter и LinkedIn
"""

import sys
import os
from colorama import init, Fore, Style
from datetime import datetime
import json

init(autoreset=True)

def print_banner():
    """Печатает баннер приложения"""
    banner = f"""
{Fore.CYAN}╔═══════════════════════════════════════════════════════╗
║                                                       ║
║   {Fore.YELLOW}🚀 Reddit SaaS Validator{Fore.CYAN}                           ║
║                                                       ║
║   {Fore.WHITE}Мультиплатформенная валидация идей за 48 часов{Fore.CYAN}     ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝{Style.RESET_ALL}
    """
    print(banner)

def check_credentials():
    """Проверяет наличие файла .env с credentials"""
    if not os.path.exists('.env'):
        print(f"{Fore.RED}❌ Файл .env не найден!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}ℹ️  Запустите: python quick_start.py{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}   или скопируйте .env.example в .env и заполните credentials{Style.RESET_ALL}")
        return False
    return True

def get_idea_keywords(idea):
    """
    Генерирует ключевые слова для поиска на основе идеи
    """
    # Базовые ключевые слова
    keywords = [idea]
    
    # Добавляем варианты
    if ' ' in idea:
        # Если идея из нескольких слов, добавляем их по отдельности
        words = idea.split()
        keywords.extend(words)
    
    # Добавляем общие SaaS термины
    keywords.extend([
        f"{idea} tool",
        f"{idea} software",
        f"{idea} platform",
        f"{idea} alternative"
    ])
    
    return keywords[:10]  # Ограничиваем 10 ключевыми словами

def get_relevant_subreddits(idea):
    """
    Определяет релевантные subreddits на основе идеи
    """
    # Общие SaaS subreddits
    base_subreddits = ['SaaS', 'Entrepreneur', 'startups', 'smallbusiness']
    
    # Добавляем специфичные на основе ключевых слов
    idea_lower = idea.lower()
    
    specific_subreddits = {
        'marketing': ['marketing', 'digitalmarketing', 'growthmarketing'],
        'email': ['marketing', 'sales', 'EmailMarketing'],
        'crm': ['sales', 'CustomerSuccess'],
        'project': ['projectmanagement', 'productivity'],
        'design': ['web_design', 'UI_Design', 'UXDesign'],
        'dev': ['webdev', 'programming', 'coding'],
        'analytics': ['analytics', 'datascience', 'dataengineering'],
        'hr': ['humanresources', 'recruiting'],
        'finance': ['accounting', 'financialplanning'],
    }
    
    for keyword, subreddits in specific_subreddits.items():
        if keyword in idea_lower:
            base_subreddits.extend(subreddits)
    
    # Убираем дубликаты
    return list(set(base_subreddits))[:10]  # Макс 10 subreddits

def run_validation(idea, platforms, credentials):
    """
    Запускает валидацию на выбранных платформах
    
    Args:
        idea: название идеи
        platforms: список платформ ['reddit', 'twitter', 'linkedin']
        credentials: словарь с credentials
        
    Returns:
        dict с результатами валидации
    """
    from src.multiplatform_validator import MultiPlatformValidator
    
    # Подготовка keywords и subreddits
    keywords = get_idea_keywords(idea)
    subreddits = get_relevant_subreddits(idea)
    
    print(f"{Fore.CYAN}🔍 Ключевые слова:{Style.RESET_ALL}")
    for kw in keywords[:5]:
        print(f"   • {kw}")
    
    print(f"\n{Fore.CYAN}📱 Subreddits:{Style.RESET_ALL}")
    for sub in subreddits[:5]:
        print(f"   • r/{sub}")
    
    print(f"\n{Fore.CYAN}🌐 Платформы:{Style.RESET_ALL}")
    for platform in platforms:
        print(f"   • {platform.title()}")
    
    print(f"\n{Fore.YELLOW}⏳ Начинаем анализ...{Style.RESET_ALL}\n")
    
    # Подготовка credentials для каждой платформы
    reddit_creds = None
    twitter_creds = None
    linkedin_creds = None
    
    if 'reddit' in platforms and credentials.get('REDDIT_CLIENT_ID'):
        reddit_creds = {
            'client_id': credentials['REDDIT_CLIENT_ID'],
            'client_secret': credentials['REDDIT_CLIENT_SECRET'],
            'user_agent': credentials['REDDIT_USER_AGENT']
        }
    
    if 'twitter' in platforms and credentials.get('TWITTER_BEARER_TOKEN'):
        twitter_creds = {
            'bearer_token': credentials['TWITTER_BEARER_TOKEN']
        }
    
    if 'linkedin' in platforms and credentials.get('LINKEDIN_EMAIL'):
        linkedin_creds = {
            'email': credentials['LINKEDIN_EMAIL'],
            'password': credentials['LINKEDIN_PASSWORD']
        }
    
    # Инициализация validator
    validator = MultiPlatformValidator(
        reddit_creds=reddit_creds,
        twitter_creds=twitter_creds,
        linkedin_creds=linkedin_creds
    )
    
    # Запуск валидации
    results = validator.validate_idea(
        idea_name=idea,
        keywords=keywords,
        subreddits=subreddits if 'reddit' in platforms else [],
        target_job_titles=['CEO', 'CTO', 'Product Manager', 'Marketing Manager'] if 'linkedin' in platforms else None,
        competitor_names=[]  # Можно добавить интерактивный ввод
    )
    
    return results

def print_results(results):
    """
    Выводит результаты валидации в терминал
    """
    print(f"\n{'='*60}")
    print(f"{Fore.CYAN}📊 РЕЗУЛЬТАТЫ ВАЛИДАЦИИ{Style.RESET_ALL}")
    print(f"{'='*60}\n")
    
    # Общая оценка
    score = results.get('overall_score', 0)
    verdict = results.get('verdict', 'N/A')
    
    # Цвет в зависимости от оценки
    if score >= 80:
        score_color = Fore.GREEN
        emoji = "🚀"
    elif score >= 60:
        score_color = Fore.YELLOW
        emoji = "✅"
    elif score >= 40:
        score_color = Fore.YELLOW
        emoji = "⚠️"
    else:
        score_color = Fore.RED
        emoji = "❌"
    
    print(f"{emoji} {score_color}Оценка: {score}/100{Style.RESET_ALL}")
    print(f"📋 {verdict}\n")
    
    # Статистика по платформам
    print(f"{Fore.CYAN}📈 Статистика по платформам:{Style.RESET_ALL}\n")
    
    if 'reddit' in results.get('platforms_analyzed', []):
        reddit_data = results.get('reddit_data', {})
        print(f"  {Fore.BLUE}Reddit:{Style.RESET_ALL}")
        print(f"    • Постов найдено: {reddit_data.get('posts_found', 0)}")
        print(f"    • Болевых точек: {reddit_data.get('pain_points', 0)}")
        print(f"    • Размер аудитории: {reddit_data.get('market_size', 0):,}")
        print()
    
    if 'twitter' in results.get('platforms_analyzed', []):
        twitter_data = results.get('twitter_data', {})
        print(f"  {Fore.CYAN}Twitter/X:{Style.RESET_ALL}")
        print(f"    • Твитов найдено: {twitter_data.get('tweets_found', 0)}")
        print(f"    • Болевых точек: {twitter_data.get('pain_points', 0)}")
        print(f"    • Средний engagement: {twitter_data.get('avg_engagement', 0):.1f}")
        print()
    
    if 'linkedin' in results.get('platforms_analyzed', []):
        linkedin_data = results.get('linkedin_data', {})
        print(f"  {Fore.MAGENTA}LinkedIn:{Style.RESET_ALL}")
        print(f"    • Целевая аудитория: {linkedin_data.get('market_size', 0)} профилей")
        print(f"    • Конкурентов найдено: {linkedin_data.get('competitors', 0)}")
        print()
    
    # Топ инсайты
    if results.get('key_insights'):
        print(f"{Fore.CYAN}💡 Ключевые инсайты:{Style.RESET_ALL}\n")
        for insight in results['key_insights'][:5]:
            print(f"  • {insight}")
        print()
    
    # Рекомендации
    if results.get('recommendations'):
        print(f"{Fore.CYAN}🎯 Рекомендации:{Style.RESET_ALL}\n")
        for rec in results['recommendations'][:5]:
            print(f"  • {rec}")
        print()

def save_results(results, idea):
    """
    Сохраняет результаты в файл
    """
    # Создаём папку results если её нет
    os.makedirs('results', exist_ok=True)
    
    # Генерируем имя файла
    safe_idea = idea.replace(' ', '_').replace('/', '_')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"results/{safe_idea}_{timestamp}.json"
    
    # Сохраняем
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    
    return filename

def main():
    """Главная функция CLI"""
    print_banner()
    
    # Проверка credentials
    if not check_credentials():
        sys.exit(1)
    
    # Загрузка переменных окружения
    from dotenv import load_dotenv
    load_dotenv()
    
    # Загружаем credentials
    credentials = {
        'REDDIT_CLIENT_ID': os.getenv('REDDIT_CLIENT_ID'),
        'REDDIT_CLIENT_SECRET': os.getenv('REDDIT_CLIENT_SECRET'),
        'REDDIT_USER_AGENT': os.getenv('REDDIT_USER_AGENT'),
        'TWITTER_BEARER_TOKEN': os.getenv('TWITTER_BEARER_TOKEN'),
        'LINKEDIN_EMAIL': os.getenv('LINKEDIN_EMAIL'),
        'LINKEDIN_PASSWORD': os.getenv('LINKEDIN_PASSWORD'),
    }
    
    # Проверяем какие платформы доступны
    available_platforms = []
    if credentials['REDDIT_CLIENT_ID']:
        available_platforms.append('reddit')
    if credentials['TWITTER_BEARER_TOKEN']:
        available_platforms.append('twitter')
    if credentials['LINKEDIN_EMAIL']:
        available_platforms.append('linkedin')
    
    if not available_platforms:
        print(f"{Fore.RED}❌ Не найдены credentials ни для одной платформы!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}ℹ️  Запустите: python quick_start.py{Style.RESET_ALL}")
        sys.exit(1)
    
    print(f"\n{Fore.GREEN}✓ Credentials загружены{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Доступные платформы:{Style.RESET_ALL} {', '.join(available_platforms)}\n")
    
    # Импорты (после проверки credentials)
    try:
        from src.multiplatform_validator import MultiPlatformValidator
    except ImportError as e:
        print(f"{Fore.RED}❌ Модули не найдены: {e}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}   Установите зависимости: pip install -r requirements.txt{Style.RESET_ALL}")
        sys.exit(1)
    
    # Парсинг аргументов
    import argparse
    parser = argparse.ArgumentParser(description='Валидация SaaS идей')
    parser.add_argument('idea', nargs='?', help='Название SaaS идеи')
    parser.add_argument('--reddit-only', action='store_true', help='Только Reddit')
    parser.add_argument('--twitter-only', action='store_true', help='Только Twitter')
    parser.add_argument('--linkedin-only', action='store_true', help='Только LinkedIn')
    parser.add_argument('--output', '-o', help='Файл для сохранения результатов')
    
    args = parser.parse_args()
    
    # Определяем какие платформы использовать
    if args.reddit_only:
        platforms = ['reddit']
    elif args.twitter_only:
        platforms = ['twitter']
    elif args.linkedin_only:
        platforms = ['linkedin']
    else:
        platforms = available_platforms  # Все доступные
    
    # Фильтруем только доступные платформы
    platforms = [p for p in platforms if p in available_platforms]
    
    if not platforms:
        print(f"{Fore.RED}❌ Выбранные платформы недоступны (нет credentials){Style.RESET_ALL}")
        sys.exit(1)
    
    # Если идея не указана, запрашиваем интерактивно
    if not args.idea:
        print(f"\n{Fore.CYAN}💡 Введите вашу SaaS идею:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}   (например: \"email marketing automation\" или \"project management tool\"){Style.RESET_ALL}")
        idea = input(f"\n{Fore.WHITE}> {Style.RESET_ALL}").strip()
        if not idea:
            print(f"{Fore.RED}❌ Идея не указана!{Style.RESET_ALL}")
            sys.exit(1)
    else:
        idea = args.idea
    
    print(f"\n{Fore.CYAN}📊 Анализируем идею:{Fore.WHITE} {idea}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}⏳ Это займёт 5-15 минут в зависимости от количества платформ...{Style.RESET_ALL}\n")
    
    # Запуск валидации
    try:
        results = run_validation(idea, platforms, credentials)
        
        # Вывод результатов
        print_results(results)
        
        # Сохранение результатов
        if args.output:
            filename = args.output
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        else:
            filename = save_results(results, idea)
        
        print(f"\n{Fore.GREEN}✓ Анализ завершён!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📄 Результаты сохранены в: {Fore.WHITE}{filename}{Style.RESET_ALL}")
        
        # Финальная рекомендация
        score = results.get('overall_score', 0)
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        if score >= 80:
            print(f"{Fore.GREEN}🚀 ОТЛИЧНАЯ ИДЕЯ! Рекомендуем двигаться вперёд.{Style.RESET_ALL}")
        elif score >= 60:
            print(f"{Fore.YELLOW}✅ ХОРОШАЯ ИДЕЯ! Есть потенциал, уточните детали.{Style.RESET_ALL}")
        elif score >= 40:
            print(f"{Fore.YELLOW}⚠️ СРЕДНЯЯ ИДЕЯ. Нужны дополнительные исследования.{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ СЛАБАЯ ВАЛИДАЦИЯ. Рекомендуем пересмотреть идею.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}⚠️  Прервано пользователем{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}❌ Ошибка во время анализа: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}⚠️  Прервано пользователем{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}❌ Ошибка: {e}{Style.RESET_ALL}")
        sys.exit(1)
