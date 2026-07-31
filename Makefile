.PHONY: check research-validate research-rebuild

check: research-validate

research-validate:
	python3 coursework/case-study/research/scripts/validation/validate_qual_data.py
	python3 -c "from pathlib import Path; required=['coursework/missions/README.md','coursework/missions/submission-registry.md','coursework/case-study/research/docs/project/research_plan.md','coursework/case-study/research/docs/project/timeline.md','coursework/case-study/research/data/synthesis/qualitative_cards.csv','coursework/case-study/product/product-brief.md','coursework/case-study/design/figma-index.md','coursework/portfolio/story/case-study-outline.md']; missing=[p for p in required if not Path(p).is_file()]; briefs=list(Path('coursework/missions').glob('mission-*/brief-verbatim.md')); assert not missing, missing; assert len(briefs)==10, len(briefs); print('WORKSPACE QA PASS')"

research-rebuild:
	python3 coursework/case-study/research/scripts/analysis/code_munto.py
	python3 coursework/case-study/research/scripts/analysis/analyze_google_play_review_history.py
	python3 coursework/case-study/research/scripts/analysis/code_google_play_reviews.py
	python3 coursework/case-study/research/scripts/analysis/summarize_google_play_coding.py
	python3 coursework/case-study/research/scripts/validation/verify_and_merge_google_play_cards.py
	python3 coursework/case-study/research/scripts/analysis/code_app_store_reviews.py
	python3 coursework/case-study/research/scripts/analysis/merge_app_store_comparison.py
	$(MAKE) research-validate
