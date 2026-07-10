import { useState } from 'react';
import {
  Button,
  Header,
  Icon,
  ThemeProvider,
} from '@beeline/design-system-react';
import { Icons } from '@beeline/design-tokens/js/iconfont';

import './App.scss';

/** Имя продукта в шапке — задайте под своё приложение */
export const APP_PRODUCT_NAME = 'App';

function App() {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'light' ? 'dark' : 'light'));
  };

  return (
    <ThemeProvider isRoot theme={theme}>
      <div className="app-root">
        <Header
          nameProduct={APP_PRODUCT_NAME}
          nameLogo="logoThemeable"
          iconsList={
            <Button
              variant="outlined"
              size="small"
              onClick={toggleTheme}
              aria-label={
                theme === 'light'
                  ? 'Включить тёмную тему'
                  : 'Включить светлую тему'
              }
            >
              {theme === 'light' ? (
                <Icon iconName={Icons.HalfMoon} />
              ) : (
                <Icon iconName={Icons.Sun} />
              )}
            </Button>
          }
        />
        {/* Сюда — маршруты, страницы, контент приложения */}
        <main className="app-main" />
      </div>
    </ThemeProvider>
  );
}

export default App;
