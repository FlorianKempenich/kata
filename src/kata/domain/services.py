import re
from pathlib import Path
from typing import Optional

from kata import config
from kata.data.repos import KataTemplateRepo, KataLanguageRepo
from kata.domain.exceptions import InvalidKataName, KataLanguageNotFound, KataTemplateTemplateNameNotFound
from kata.domain.grepo import GRepo


class InitKataService:
    def __init__(self, kata_language_repo: KataLanguageRepo, kata_template_repo: KataTemplateRepo, grepo: GRepo):
        self._kata_language_repo = kata_language_repo
        self._kata_template_repo = kata_template_repo
        self._grepo = grepo

    def init_kata(self, parent_dir: Path, kata_name: str, template_language: str, template_name: Optional[str]) -> None:
        self._validate_parent_dir(parent_dir)
        self._validate_kata_name(kata_name)

        kata_template = self._get_kata_template(template_language, template_name)
        path = self._build_path(kata_template)
        files_to_download = self._grepo.get_files_to_download(user=config.KATA_GITHUB_REPO_USER,
                                                              repo=config.KATA_GITHUB_REPO_REPO,
                                                              path=path)
        kata_dir = parent_dir / kata_name
        self._grepo.download_files_at_location(kata_dir, files_to_download)

    @staticmethod
    def _validate_parent_dir(parent_dir):
        if not parent_dir.exists():
            raise FileNotFoundError(f"Invalid Directory: '{parent_dir.absolute()}'")

    @staticmethod
    def _validate_kata_name(kata_name):
        def has_spaces():
            return len(kata_name.split(' ')) > 1

        if not kata_name:
            raise InvalidKataName(kata_name, reason='empty')
        if has_spaces():
            raise InvalidKataName(kata_name, reason='contains spaces')

        if not re.match(r'^[_a-z]*$', kata_name):
            raise InvalidKataName(kata_name)

    def _get_kata_template(self, template_language: str, template_name: str):
        def get_kata_language_or_raise():
            res = self._kata_language_repo.get(template_language)
            if not res:
                raise KataLanguageNotFound()
            return res

        def only_one_available_for_language():
            return len(templates_for_language) == 1

        def first():
            return templates_for_language[0]

        def first_found_or_raise(exception):
            for template in templates_for_language:
                if template.template_name == template_name:
                    return template
            raise exception()

        kata_language = get_kata_language_or_raise()
        templates_for_language = self._kata_template_repo.get_for_language(kata_language)
        if only_one_available_for_language():
            return first()
        else:
            return first_found_or_raise(KataTemplateTemplateNameNotFound)

    @staticmethod
    def _build_path(kata_template):
        path = kata_template.language.name
        if kata_template.template_name:
            path += '/' + kata_template.template_name
        return path
