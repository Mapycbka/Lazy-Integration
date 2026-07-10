"""Главное окно приложения."""

from __future__ import annotations

import traceback
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.constants import (
    APP_TITLE,
    BBU_TYPES,
    REGIONS_BY_SITE_TYPE,
    SITE_TYPES,
    TEMPLATES_DIR,
    TEMP_DIR,
    WINDOW_DEFAULT_HEIGHT,
    WINDOW_DEFAULT_WIDTH,
    WINDOW_MIN_HEIGHT,
    WINDOW_MIN_WIDTH,
)
from core.mapping_engine import MappingEngine
from core.excel_loader import ExcelLoader
from core.validators import TransportDataError, ValidationError
from config.software_options import BSC_SOFTWARE_OPTIONS, BTS_SOFTWARE_OPTIONS
from gui.dialogs import RRUChainPortDialog, TransportIssueChoiceDialog, TransportManualInputDialog
from gui.widgets import FilePickerRow, LogViewer, StatusBarWidget
from models.app_state import GenerationArtifacts, UserInputState
from utils.logger import setup_logger


class MainWindow(QMainWindow):
    """Главное окно с выбором файлов и запуском формирования."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.resize(WINDOW_DEFAULT_WIDTH, WINDOW_DEFAULT_HEIGHT)

        self.state = UserInputState()
        self.artifacts = GenerationArtifacts()
        self.logger = setup_logger(self.append_log)
        self.engine = MappingEngine(self.logger)
        self.di_excel_loader = ExcelLoader()

        self._build_ui()
        self._connect_signals()
        self._refresh_regions()
        self._sync_state_to_ui()
        self._update_form_availability()

        self.logger.info("Приложение запущено.")

    def _build_ui(self) -> None:
        central = QWidget()
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(14)

        files_group = QGroupBox("Файлы")
        files_layout = QVBoxLayout(files_group)
        self.di_picker = FilePickerRow("Загрузить файл ДИ", "Файл ДИ не выбран")
        self.ts_picker = FilePickerRow("Загрузить файл ТС", "Файл ТС не выбран")
        self.skip_ts_checkbox = QCheckBox("Пропустить загрузку ТС-параметрики")
        files_layout.addWidget(self.di_picker)
        files_layout.addWidget(self.ts_picker)
        files_layout.addWidget(self.skip_ts_checkbox)

        bsc_info_group = QGroupBox("Интегрируемая станция")
        bsc_info_layout = QFormLayout(bsc_info_group)
        self.bsc_name_label = QLabel("—")
        bsc_info_layout.addRow("BSC:", self.bsc_name_label)

        params_group = QGroupBox("Параметры формирования")
        params_layout = QFormLayout(params_group)

        self.site_type_combo = QComboBox()
        self.site_type_combo.addItems(SITE_TYPES)

        self.region_combo = QComboBox()
        self.bbu_type_combo = QComboBox()
        self.bbu_type_combo.addItems(BBU_TYPES)
        self.template_combo = QComboBox()
        self.bts_software_combo = QComboBox()
        self.bts_software_combo.addItems(BTS_SOFTWARE_OPTIONS)
        self.bsc_software_combo = QComboBox()
        self.bsc_software_combo.addItems(BSC_SOFTWARE_OPTIONS)

        self.slot_edit = QLineEdit()
        self.slot_edit.setPlaceholderText("Например: 1-2 или 1,2")

        self.ports_edit = QLineEdit()
        self.ports_edit.setPlaceholderText("Например: 0-2 или 0,1,2")

        self.transport_port_combo = QComboBox()
        self.transport_port_combo.addItems(["0", "1"])

        params_layout.addRow("Тип площадки:", self.site_type_combo)
        params_layout.addRow("Регион:", self.region_combo)
        params_layout.addRow("Тип BBU:", self.bbu_type_combo)
        params_layout.addRow("Шаблон:", self.template_combo)
        params_layout.addRow("Софт BTS:", self.bts_software_combo)
        params_layout.addRow("Софт BSC:", self.bsc_software_combo)
        params_layout.addRow("Номер слота платы:", self.slot_edit)
        params_layout.addRow("Используемые порты платы:", self.ports_edit)
        params_layout.addRow("Порт транспортной платы:", self.transport_port_combo)

        buttons_layout = QHBoxLayout()
        self.generate_button = QPushButton("Сформировать файл")
        self.save_button = QPushButton("Сохранить результат")
        self.save_button.setEnabled(False)
        self.clear_temp_button = QPushButton("Очистить temp")
        buttons_layout.addWidget(self.generate_button)
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.clear_temp_button)

        self.status_widget = StatusBarWidget()

        info_label = QLabel(
            "Приложение считывает данные из ДИ, создает копию шаблона, заполняет листы "
            "по бизнес-правилам и сохраняет оригинал шаблона без изменений."
        )
        info_label.setWordWrap(True)
        info_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        logs_group = QGroupBox("Логи выполнения")
        logs_layout = QVBoxLayout(logs_group)
        self.log_viewer = LogViewer()
        logs_layout.addWidget(self.log_viewer)

        main_layout.addWidget(files_group)
        main_layout.addWidget(bsc_info_group)
        main_layout.addWidget(params_group)
        main_layout.addLayout(buttons_layout)
        main_layout.addWidget(self.status_widget)
        main_layout.addWidget(info_label)
        main_layout.addWidget(logs_group, stretch=1)

        self.setCentralWidget(central)

    def _connect_signals(self) -> None:
        self.di_picker.button.clicked.connect(self.select_di_file)
        self.ts_picker.button.clicked.connect(self.select_ts_file)
        self.skip_ts_checkbox.toggled.connect(self._on_skip_ts_toggled)
        self.site_type_combo.currentIndexChanged.connect(self._refresh_regions)
        self.site_type_combo.currentIndexChanged.connect(self._refresh_templates)
        self.site_type_combo.currentIndexChanged.connect(self._sync_state_to_ui)
        self.region_combo.currentIndexChanged.connect(self._sync_state_to_ui)
        self.region_combo.currentIndexChanged.connect(self._refresh_templates)
        self.bbu_type_combo.currentIndexChanged.connect(self._refresh_templates)
        self.bbu_type_combo.currentIndexChanged.connect(self._sync_state_to_ui)
        self.template_combo.currentIndexChanged.connect(self._sync_state_to_ui)
        self.bts_software_combo.currentIndexChanged.connect(self._sync_state_to_ui)
        self.bsc_software_combo.currentIndexChanged.connect(self._sync_state_to_ui)
        self.slot_edit.textChanged.connect(self._sync_state_to_ui)
        self.ports_edit.textChanged.connect(self._sync_state_to_ui)
        self.transport_port_combo.currentIndexChanged.connect(self._sync_state_to_ui)
        self.generate_button.clicked.connect(self.generate_file)
        self.save_button.clicked.connect(self.save_result)
        self.clear_temp_button.clicked.connect(self.clear_temp)

    def _refresh_regions(self) -> None:
        current_site_type = self.site_type_combo.currentText()
        regions = REGIONS_BY_SITE_TYPE.get(current_site_type, ())
        self.region_combo.blockSignals(True)
        self.region_combo.clear()
        self.region_combo.addItems(regions)
        self.region_combo.blockSignals(False)
        self._refresh_templates()
        self._sync_state_to_ui()

    def _refresh_templates(self) -> None:
        region = self.region_combo.currentText().strip()
        bbu_type = self.bbu_type_combo.currentText().strip()

        templates: list[str] = []
        if region and bbu_type:
            template_dir = TEMPLATES_DIR / region / bbu_type
            if template_dir.exists():
                templates = sorted(
                    path.name
                    for path in template_dir.iterdir()
                    if path.is_file() and path.suffix.lower() in {".xlsx", ".xlsm"}
                )

        self.template_combo.blockSignals(True)
        self.template_combo.clear()
        self.template_combo.addItems(templates)
        self.template_combo.blockSignals(False)

        if templates:
            self.logger.info(
                "Загружен список шаблонов из %s/%s: %s шт.",
                region,
                bbu_type,
                len(templates),
            )
        elif region and bbu_type:
            self.logger.warning(
                "В папке templates/%s/%s шаблоны не найдены.",
                region,
                bbu_type,
            )

    def _sync_state_to_ui(self) -> None:
        self.state.site_type = self.site_type_combo.currentText()
        self.state.region = self.region_combo.currentText()
        self.state.bbu_type = self.bbu_type_combo.currentText()
        self.state.skip_ts_loading = self.skip_ts_checkbox.isChecked()
        self.state.template_name = self.template_combo.currentText()
        self.state.bts_software = self.bts_software_combo.currentText().strip()
        self.state.bsc_software = self.bsc_software_combo.currentText().strip()
        if self.state.region and self.state.bbu_type and self.state.template_name:
            self.state.template_path = str(
                TEMPLATES_DIR / self.state.region / self.state.bbu_type / self.state.template_name
            )
        else:
            self.state.template_path = ""
        self.state.slot_numbers_raw = self.slot_edit.text()
        self.state.board_ports_raw = self.ports_edit.text()
        self.state.transport_port = self.transport_port_combo.currentText()
        self._update_form_availability()

    def _update_form_availability(self) -> None:
        ready = all(
            [
                self.state.di_path,
                self.state.skip_ts_loading or self.state.ts_path,
                self.state.template_path,
                self.state.site_type,
                self.state.region,
                self.state.slot_numbers_raw.strip(),
                self.state.board_ports_raw.strip(),
            ]
        )
        self.generate_button.setEnabled(ready)

    def select_di_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл ДИ",
            "",
            "Excel Files (*.xlsx *.xlsm)",
        )
        if file_path:
            self.state.di_path = file_path
            self.di_picker.path_edit.setText(file_path)
            self.logger.info("Выбран файл ДИ: %s", file_path)
            self._extract_bsc_name_from_di(file_path)
            self._update_form_availability()

    def select_ts_file(self) -> None:
        if self.skip_ts_checkbox.isChecked():
            return
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл ТС",
            "",
            "Excel Files (*.xlsx *.xlsm)",
        )
        if file_path:
            self.state.ts_path = file_path
            self.ts_picker.path_edit.setText(file_path)
            self.logger.info("Выбран файл ТС: %s", file_path)
            self._update_form_availability()

    def _on_skip_ts_toggled(self, checked: bool) -> None:
        self.state.skip_ts_loading = checked
        self.ts_picker.button.setEnabled(not checked)
        self.ts_picker.path_edit.setEnabled(not checked)
        if checked:
            self.logger.info(
                "Включен режим пропуска ТС-параметрики. Файл будет сформирован по ДИ, "
                "а ТС-поля останутся пустыми."
            )
        self._sync_state_to_ui()

    def _extract_bsc_name_from_di(self, file_path: str) -> None:
        """Извлекает BSC NAME из листа 2G_BTS_Data файла ДИ и отображает в GUI."""
        try:
            workbook = self.di_excel_loader.open_di_workbook(file_path)
            bsc_name = self.di_excel_loader.extract_bsc_name(workbook)
            workbook.close()
            self.state.bsc_name = bsc_name
            self.bsc_name_label.setText(bsc_name or "—")
            if bsc_name:
                self.logger.info("BSC NAME: %s", bsc_name)
            else:
                self.logger.info("Столбец BSC NAME не найден или пуст в файле ДИ.")
        except Exception as error:
            self.state.bsc_name = ""
            self.bsc_name_label.setText("—")
            self.logger.warning("Не удалось прочитать BSC NAME из файла ДИ: %s", error)

    def generate_file(self) -> None:
        self.status_widget.set_status("формирование файла")
        self.generate_button.setEnabled(False)
        self.save_button.setEnabled(False)

        try:
            self.artifacts.working_copy_path = self.engine.generate_file(
                self.state,
                port_dialog_callback=self._select_rru_ports,
                transport_issue_callback=self._resolve_transport_issue,
            )
            self.save_button.setEnabled(True)
            self.status_widget.set_status("формирование завершено")
            self.logger.info("Рабочий файл сформирован: %s", self.artifacts.working_copy_path)
            QMessageBox.information(
                self,
                "Формирование завершено",
                "Файл успешно сформирован. Теперь можно сохранить результат.",
            )
        except ValidationError as error:
            self.status_widget.set_status("ошибка")
            self.logger.error(str(error))
            QMessageBox.warning(self, "Ошибка", str(error))
        except Exception as error:
            self.status_widget.set_status("ошибка")
            self.logger.error("Необработанная ошибка: %s", error)
            self.logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Критическая ошибка", str(error))
        finally:
            self.generate_button.setEnabled(True)
            self._update_form_availability()

    def save_result(self) -> None:
        if not self.artifacts.working_copy_path:
            QMessageBox.warning(self, "Нет результата", "Сначала сформируйте файл.")
            return

        default_name = self.artifacts.working_copy_path.name
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить результат",
            default_name,
            "Excel Files (*.xlsx *.xlsm)",
        )
        if not file_path:
            return

        try:
            self.artifacts.saved_result_path = self.engine.save_result(
                self.artifacts.working_copy_path,
                file_path,
            )
            self.status_widget.set_status("результат сохранен")
            self.logger.info("Результат сохранен: %s", self.artifacts.saved_result_path)
            QMessageBox.information(
                self,
                "Сохранено",
                f"Результат сохранен:\n{self.artifacts.saved_result_path}",
            )
        except ValidationError as error:
            self.status_widget.set_status("ошибка сохранения")
            self.logger.error(str(error))
            QMessageBox.warning(self, "Ошибка сохранения", str(error))

    def _select_rru_ports(
        self,
        chain_candidates: list[tuple[str, int]],
        slot_numbers: list[int],
        board_ports: list[int],
    ) -> dict[str, tuple[int, int]] | None:
        dialog = RRUChainPortDialog(chain_candidates, slot_numbers, board_ports, self)
        if dialog.exec():
            selected = dialog.get_selected_bindings()
            self.logger.info("Пользователь выбрал платы и порты RRUCHAIN: %s", selected)
            return selected
        return None

    def _resolve_transport_issue(
        self,
        error: TransportDataError,
        default_transport_data: dict[str, str],
    ) -> dict[str, str] | None:
        """Предлагает пользователю вручную ввести ТС или пропустить этот шаг."""
        choice_dialog = TransportIssueChoiceDialog(error, self)
        choice_dialog.exec()
        clicked_button = choice_dialog.clickedButton()

        if clicked_button is choice_dialog.manual_button:
            manual_dialog = TransportManualInputDialog(default_transport_data, self)
            if manual_dialog.exec():
                return manual_dialog.get_transport_data()
            return None

        if clicked_button is choice_dialog.skip_button:
            return default_transport_data

        return None

    def append_log(self, message: str) -> None:
        self.log_viewer.append(message)

    def clear_temp(self) -> None:
        """Удаляет все сгенерированные файлы из папки temp."""
        if not TEMP_DIR.exists():
            self.logger.info("Папка temp не найдена — нечего очищать.")
            return

        files = list(TEMP_DIR.glob("*_generated_*.xlsx"))
        if not files:
            self.logger.info("В папке temp нет сгенерированных файлов.")
            return

        reply = QMessageBox.question(
            self,
            "Очистка temp",
            f"Удалить {len(files)} файл(ов) из папки temp?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        removed = 0
        for f in files:
            try:
                f.unlink()
                removed += 1
            except Exception as error:
                self.logger.warning("Не удалось удалить %s: %s", f.name, error)

        self.logger.info("Удалено %d файл(ов) из папки temp.", removed)
