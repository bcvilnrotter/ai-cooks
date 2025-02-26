@echo off
echo Deploying AI Cooks to Hugging Face Spaces...
python deploy_to_huggingface.py --token-path "../.gitignore/.env" --token-key "HUGGINGFACE_TOKEN_CHANGELOG_LLM" %*
if %ERRORLEVEL% EQU 0 (
    echo Deployment completed successfully!
    echo Your application is now available at: https://huggingface.co/spaces/bcvilnrotter/ai-cooks-game
) else (
    echo Deployment failed with error code %ERRORLEVEL%
)
pause
