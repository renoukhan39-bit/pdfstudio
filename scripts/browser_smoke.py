"""Real browser acceptance tests; downloaded PDFs are reopened and checked."""
from io import BytesIO
import os
from pathlib import Path

from playwright.sync_api import sync_playwright, expect
from pypdf import PdfReader, PdfWriter
from office_fixtures import make_docx, make_pptx


def pdf(widths):
    with PdfWriter() as writer:
        for width in widths:
            writer.add_blank_page(width=width, height=300)
        data = BytesIO()
        writer.write(data)
        return data.getvalue()


def main():
    reports = Path('reports/browser')
    reports.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        context = browser.new_context(accept_downloads=True)
        context.tracing.start(screenshots=True, snapshots=True, sources=True)
        page = context.new_page()
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        try:
            page.goto(os.environ.get('PDFSTUDIO_TEST_URL', 'http://127.0.0.1:8000'))
            expect(page.locator('#tool-select option')).to_have_count(16)
            page.locator('#fileInput').set_input_files([
                {'name': 'first.pdf', 'mimeType': 'application/pdf', 'buffer': pdf([100, 200])},
                {'name': 'second.pdf', 'mimeType': 'application/pdf', 'buffer': pdf([400])},
            ])
            with page.expect_download() as download:
                page.locator('#merge-button').click()
            merged = PdfReader(download.value.path())
            assert [int(p.mediabox.width) for p in merged.pages] == [100, 200, 400]
            expect(page.locator('#use-result')).to_be_visible()
            page.locator('#use-result').click()
            page.locator('#tool-select').select_option('extract')
            page.locator('#page-selection').fill('3,1')
            with page.expect_download() as download:
                page.locator('#merge-button').click()
            assert [int(p.mediabox.width) for p in PdfReader(download.value.path()).pages] == [400, 100]
            page.locator('#use-result').click()
            page.locator('#tool-select').select_option('page-numbers')
            with page.expect_download() as download:
                page.locator('#merge-button').click()
            assert '1 / 2' in PdfReader(download.value.path()).pages[0].extract_text()
            page.locator('#tool-select').select_option('extract')
            page.locator('#page-selection').fill('999')
            page.locator('#merge-button').click()
            expect(page.locator('#merge-status')).to_have_class('merge-status error')
            expect(page.locator('#merge-button')).to_be_enabled()
            page.locator('#clear-files').click()
            expect(page.locator('#merge-button')).to_be_disabled()
            # Real browser DOCX -> PDF -> continue editing journey.
            page.locator('#tool-select').select_option('docx-to-pdf')
            page.locator('#fileInput').set_input_files({
                'name': 'example.docx',
                'mimeType': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'buffer': make_docx(),
            })
            with page.expect_download() as download:
                page.locator('#merge-button').click()
            converted = PdfReader(download.value.path())
            assert 'PDF Studio conversion smoke test' in converted.pages[0].extract_text()
            page.locator('#use-result').click()
            assert page.locator('#tool-select').input_value() == 'extract'
            expect(page.locator('#merge-button')).to_be_enabled()

            # Real browser PPTX -> PDF -> reopen -> use result in another tool.
            page.locator('#tool-select').select_option('pptx-to-pdf')
            page.locator('#fileInput').set_input_files({
                'name': 'slides.pptx',
                'mimeType': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                'buffer': make_pptx(),
            })
            with page.expect_download() as download:
                page.locator('#merge-button').click()
            converted_pptx = PdfReader(download.value.path(), strict=True)
            assert len(converted_pptx.pages) == 1
            assert 'PDF Studio PowerPoint smoke test' in (converted_pptx.pages[0].extract_text() or '')
            page.locator('#use-result').click()
            assert page.locator('#tool-select').input_value() == 'extract'
            page.locator('#page-selection').fill('1')
            with page.expect_download() as download:
                page.locator('#merge-button').click()
            chained = PdfReader(download.value.path(), strict=True)
            assert len(chained.pages) == 1
            assert 'PDF Studio PowerPoint smoke test' in (chained.pages[0].extract_text() or '')

            page.set_viewport_size({'width': 390, 'height': 844})
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            page.screenshot(path=str(reports / 'mobile.png'), full_page=True)
            assert errors == [], errors
            print('Browser PDF, DOCX/PPTX conversion, chaining, validation and mobile layout passed.')
        finally:
            context.tracing.stop(path=str(reports / 'trace.zip'))
            browser.close()


if __name__ == '__main__':
    main()
