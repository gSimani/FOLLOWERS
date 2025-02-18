from .instagram import InstagramScraper
from .facebook import FacebookScraper

class ScraperFactory:
    _scrapers = {}
    
    @classmethod
    def get_scraper(cls, platform_name, **kwargs):
        """Get or create a scraper instance for the given platform"""
        platform_name = platform_name.lower()
        
        if platform_name not in cls._scrapers:
            if platform_name == 'instagram':
                cls._scrapers[platform_name] = InstagramScraper(**kwargs)
            elif platform_name == 'facebook':
                cls._scrapers[platform_name] = FacebookScraper(**kwargs)
            else:
                raise ValueError(f"Unsupported platform: {platform_name}")
        
        return cls._scrapers[platform_name]
    
    @classmethod
    def close_all(cls):
        """Close all active scrapers"""
        for scraper in cls._scrapers.values():
            scraper.close()
        cls._scrapers.clear() 