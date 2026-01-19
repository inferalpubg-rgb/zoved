// Система интернационализации (i18n)
class I18n {
    constructor() {
        this.languages = {};
        this.currentLanguage = this.getStoredLanguage() || 'ru';
        this.init();
    }

    async init() {
        try {
            const response = await fetch('/static/languages.json');
            this.languages = await response.json();
            this.applyLanguage(this.currentLanguage);
            this.setupLanguageSwitcher();
        } catch (error) {
            console.error('Error loading languages:', error);
        }
    }

    getStoredLanguage() {
        return localStorage.getItem('language') || navigator.language.split('-')[0];
    }

    setLanguage(lang) {
        if (this.languages[lang]) {
            this.currentLanguage = lang;
            localStorage.setItem('language', lang);
            this.applyLanguage(lang);
            this.updateActiveButton(lang);
        }
    }

    applyLanguage(lang) {
        if (!this.languages[lang]) return;

        const strings = this.languages[lang];
        
        // Применяем переводы ко всем элементам с data-i18n атрибутом
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            if (strings[key]) {
                if (element.tagName === 'INPUT') {
                    element.placeholder = strings[key];
                } else if (element.tagName === 'BUTTON' || element.tagName === 'A') {
                    element.textContent = strings[key];
                } else {
                    element.textContent = strings[key];
                }
            }
        });

        // Применяем переводы к элементам с data-i18n-attr атрибутом
        document.querySelectorAll('[data-i18n-attr]').forEach(element => {
            const attrs = element.getAttribute('data-i18n-attr').split(',');
            attrs.forEach(attr => {
                const [key, attrName] = attr.trim().split(':');
                if (strings[key]) {
                    element.setAttribute(attrName, strings[key]);
                }
            });
        });

        // Устанавливаем язык для HTML
        document.documentElement.lang = lang;
        document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';
    }

    setupLanguageSwitcher() {
        const switcherContainer = document.querySelector('.language-switcher');
        if (!switcherContainer) {
            this.createLanguageSwitcher();
        }

        // Добавляем обработчики для существующих кнопок
        document.querySelectorAll('.lang-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const lang = e.target.getAttribute('data-lang');
                if (lang) {
                    this.setLanguage(lang);
                }
            });
        });

        this.updateActiveButton(this.currentLanguage);
    }

    createLanguageSwitcher() {
        const container = document.createElement('div');
        container.className = 'language-switcher';
        
        const languages = ['ru', 'en', 'zh', 'ja', 'ko'];
        const languageNames = {
            'ru': '🇷🇺',
            'en': '🇬🇧',
            'zh': '🇨🇳',
            'ja': '🇯🇵',
            'ko': '🇰🇷'
        };

        languages.forEach(lang => {
            const btn = document.createElement('button');
            btn.className = 'lang-btn';
            btn.setAttribute('data-lang', lang);
            btn.textContent = languageNames[lang];
            btn.title = this.languages[lang]?.language || lang;
            container.appendChild(btn);
        });

        document.body.appendChild(container);
        
        // Переподключаем слушатели
        this.setupLanguageSwitcher();
    }

    updateActiveButton(lang) {
        document.querySelectorAll('.lang-btn').forEach(btn => {
            if (btn.getAttribute('data-lang') === lang) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
    }

    t(key) {
        return this.languages[this.currentLanguage]?.[key] || key;
    }
}

// Инициализируем i18n когда DOM готов
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.i18n = new I18n();
    });
} else {
    window.i18n = new I18n();
}
