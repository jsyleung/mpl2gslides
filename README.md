# mpl2gslides

Draw Matplotlib plots in Google Slides using the API.

This library converts plot elements into native objects in Google Slides (lines, shapes, groups) and inserts them into a presentation. Useful for scalable, editable slide exports.

---

## Installation

Install from source:

```bash
pip install .
```

Or, in development mode:

```bash
pip install -e .
```

## Google API Setup

To use the Google Slides API, you’ll need to authenticate with your own Google account:
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project or select an existing one.
3. Enable *both* the **Google Slides API** and **Google Drive API**.
4. Go to **APIs & Services** → **Credentials**.
5. Create an **OAuth 2.0 Client ID** (type: Desktop App).
6. Download the `credentials.json` file.
7. On first run, a browser will open asking for permission. A `token.json` will be saved for future sessions.

**Tip:** Set the `GSLIDES_CREDENTIALS` and `GSLIDES_TOKEN` environment variables as paths to your credentials and token. Otherwise, you’ll have to provide the paths in your script.

## Usage

```python
import mpl2gslides
```

See examples in the `examples/` directory.

## License

This project is licensed under the **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)** license.

> This means you can use, modify, and share the code for **non-commercial purposes only**, with attribution.

See [LICENSE](LICENSE) for full details.
