# La Rotación · Bootcamp Java

Mi bootcamp personal de Java: 17 semanas (más una opcional) en las que cada tema sigue la misma rotación:

1. **Construir**: implementarlo desde cero.
2. **Medir**: compararlo con la versión de Java usando números reales.
3. **Aplicar**: usarlo en un problema donde sea la mejor opción.
4. **Explicar**: contarlo con mis palabras, como a un compañero.

El proyecto que hila todo el bootcamp es un tracker de hábitos que acaba siendo una API REST hecha solo con el JDK.

## Publicarlo con GitHub Pages

1. Crea un repositorio (por ejemplo `la-rotacion`) y sube todos los archivos de esta carpeta tal cual, con `index.html` en la raíz.
2. En el repositorio: **Settings → Pages → Build and deployment → Source: Deploy from a branch**. Elige la rama `main` y la carpeta `/ (root)` y pulsa **Save**.
3. En uno o dos minutos la web estará en `https://<tu-usuario>.github.io/la-rotacion/`.

## Instalarla como app de escritorio

Abre la web en Chrome o Edge:

- **Chrome:** el icono de instalar de la barra de direcciones, o el menú **⋮ → Enviar, guardar y compartir → Instalar página como aplicación**.
- **Edge:** menú **⋯ → Aplicaciones → Instalar este sitio como aplicación**.

Se abre en su propia ventana, con acceso directo en el escritorio y en el menú de inicio, y funciona sin conexión. Haciendo clic derecho en el icono de la barra de tareas tienes accesos rápidos a la hoja de personaje y a la libreta.

## Dónde se guarda el progreso

En el navegador (localStorage), en ese dispositivo. **No se sube nada a GitHub**: el repositorio solo tiene el temario y la web.

- Si borras los datos de navegación del sitio, el progreso se pierde. En **Guardado → Descargar copia** te llevas un `.json` con todo (progreso, logros y libreta), y la propia web te avisa si llevas tiempo sin hacer copia.
- Para cambiar de dispositivo o de navegador: descarga una copia en uno y restáurala en el otro (**Guardado → Restaurar**).
- La app instalada y la pestaña del mismo navegador comparten los datos.

## Editar el temario

El contenido está en `contenido/*.txt`, en un formato de texto sencillo (las claves son `titulo:`, `reto:`, `pista1:`…, y los textos largos admiten Markdown básico). Después de editar:

```bash
python3 build.py
```

Esto regenera `index.html` a partir de `plantilla.html` y del temario. Haz commit y push, y GitHub Pages se actualiza solo. Si cambias algo y no lo ves en la app instalada, recarga una vez la página: la web busca primero la versión más reciente en la red.

## Archivos

| Archivo | Qué es |
| --- | --- |
| `index.html` | La web completa (generada por `build.py`). |
| `plantilla.html` | Diseño y lógica: XP, niveles, logros, libreta y guardado. |
| `contenido/` | El temario, semana a semana. |
| `build.py` | Junta temario y plantilla en `index.html`. |
| `manifest.webmanifest`, `sw.js`, `icons/` | Lo que la hace instalable y usable sin conexión. |
