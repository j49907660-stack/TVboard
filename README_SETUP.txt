MOC InfoBoard — GitHub Actions JPG setup

1. Upload these files to your existing PUBLIC TVboard repository, keeping their paths:
   - MOC_InfoBoard.html (replaces the current file)
   - convert_pdf.py (repository root)
   - .github/workflows/update-slides.yml (exact subfolders)

2. GitHub repository > Settings > Secrets and variables > Actions > New repository secret.
   Name: MOC_PDF_ENDPOINT
   Value: the complete existing Power Automate HTTP trigger URL, including its sig parameter.
   Never paste the URL into the HTML or public repository.

3. GitHub > Settings > Actions > General > Workflow permissions:
   choose Read and write permissions (if permitted by organization policy).
   Save.

4. GitHub > Actions > Update MOC TV slides > Run workflow > Run workflow.
   Check for a green success mark. A slides folder with JPGs and slides.json should appear.

5. Open https://j49907660-stack.github.io/TVboard/MOC_InfoBoard.html?v=4
   on your LG signage screen. It will now display JPGs, not render PDF.

6. GitHub Actions checks for updates every four hours (scheduled runs may be delayed).
   The player checks slides.json every four hours; reload the page for an immediate check.

SECURITY: JPG images published on public GitHub Pages are publicly accessible.
Only use this with material approved for public access. If your HSE presentation
is internal-only, stop and choose an authenticated/private hosting solution.
Rotate the Power Automate trigger secret if it has previously been committed publicly.

NOTE: If Power Automate returns a JSON wrapper instead of raw application/pdf,
this script will stop with a clear error. Do not alter the flow before testing.
