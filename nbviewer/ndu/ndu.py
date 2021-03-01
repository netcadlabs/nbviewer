from traitlets import Unicode, HasTraits

from nbviewer.providers import _load_handler_from_location


class NDU(HasTraits):
    notebooks_upload_handler = Unicode(
        default_value="nbviewer.ndu.handlers.notebooks_handler.NotebooksHandler",
        help="The Tornado handler to allow upload and managing uploaded notebooks.",
    ).tag(config=True)

    notebooks_output_handler = Unicode(
        default_value="nbviewer.ndu.handlers.output_handler.NotebookHtmlOutputHandler",
        help="The Tornado handler to show output of notebooks.",
    ).tag(config=True)

    notebooks_download_handler = Unicode(
        default_value="nbviewer.ndu.handlers.download_handler.DownloadHandler",
        help="The Tornado handler to download notebooks.",
    ).tag(config=True)

    login_handler = Unicode(
        default_value="nbviewer.ndu.handlers.login_handler.LoginHandler",
        help="The Tornado handler to show login page.",
    ).tag(config=True)

    def get_ndu_handlers(self):
        # ndu_handler_names = dict(
        #     notebooks_upload_handler=self.notebooks_upload_handler,
        #     notebooks_output_handler=self.notebooks_output_handler,
        #     notebooks_download_handler=self.notebooks_download_handler,
        #     login_handler=self.login_handler
        # )

        notebooks_upload_handler = _load_handler_from_location(self.notebooks_upload_handler)
        notebooks_output_handler = _load_handler_from_location(self.notebooks_output_handler)
        notebooks_download_handler = _load_handler_from_location(self.notebooks_download_handler)
        login_handler = _load_handler_from_location(self.login_handler)

        pre_providers = [
            (r"/notebooks/?(.*)", notebooks_upload_handler, {}),
            (r"/outputs/?(.*)", notebooks_output_handler, {}),
            (r"/download/?(.*)", notebooks_download_handler, {}),
            (r"/login/?(.*)", login_handler, {}),
        ]

        return pre_providers
