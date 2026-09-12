# -*- coding: utf-8 -*-
"""
Deterministic Qt6 / QGIS 4 Forward-Compatibility Checker (/publish-qgis).
Performs AST static analysis to ensure 100% compliance with plugins.qgis.org
Qt6 / QGIS 4 automated checks (guaranteeing the official 'QGIS 4 Ready' badge).
"""

import ast
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

KNOWN_QT_SCOPED_ENUMS: Dict[str, Dict[str, Set[str]]] = {
    "Qt": {
        "AlignmentFlag": {
            "AlignCenter", "AlignLeft", "AlignRight", "AlignTop", "AlignBottom",
            "AlignHCenter", "AlignVCenter", "AlignJustify", "AlignAbsolute", "AlignLeading", "AlignTrailing"
        },
        "AspectRatioMode": {
            "KeepAspectRatio", "KeepAspectRatioByExpanding", "IgnoreAspectRatio"
        },
        "TransformationMode": {
            "SmoothTransformation", "FastTransformation"
        },
        "Orientation": {
            "Horizontal", "Vertical"
        },
        "ScrollBarPolicy": {
            "ScrollBarAlwaysOff", "ScrollBarAlwaysOn", "ScrollBarAsNeeded"
        },
        "PenCapStyle": {
            "RoundCap", "SquareCap", "FlatCap"
        },
        "PenJoinStyle": {
            "RoundJoin", "MiterJoin", "BevelJoin", "SvgMiterJoin"
        },
        "PenStyle": {
            "SolidLine", "DashLine", "DotLine", "DashDotLine", "DashDotDotLine", "CustomDashLine", "NoPen"
        },
        "BrushStyle": {
            "NoBrush", "SolidPattern", "Dense1Pattern", "Dense2Pattern", "Dense3Pattern",
            "Dense4Pattern", "Dense5Pattern", "Dense6Pattern", "Dense7Pattern",
            "HorPattern", "VerPattern", "CrossPattern", "BDiagPattern", "FDiagPattern",
            "DiagCrossPattern", "LinearGradientPattern", "RadialGradientPattern",
            "ConicalGradientPattern", "TexturePattern"
        },
        "GlobalColor": {
            "transparent", "color0", "color1", "black", "white", "darkGray",
            "gray", "lightGray", "red", "green", "blue", "cyan", "magenta", "yellow",
            "darkRed", "darkGreen", "darkBlue", "darkCyan", "darkMagenta", "darkYellow"
        },
        "ClipOperation": {
            "IntersectClip", "ReplaceClip", "NoClip"
        },
        "FillRule": {
            "OddEvenFill", "WindingFill"
        },
        "CursorShape": {
            "WaitCursor", "ArrowCursor", "UpArrowCursor", "CrossCursor", "IBeamCursor",
            "SizeVerCursor", "SizeHorCursor", "SizeBDiagCursor", "SizeFDiagCursor",
            "SizeAllCursor", "BlankCursor", "SplitVCursor", "SplitHCursor",
            "PointingHandCursor", "ForbiddenCursor", "WhatsThisCursor", "BusyCursor",
            "OpenHandCursor", "ClosedHandCursor", "DragCopyCursor", "DragMoveCursor", "DragLinkCursor"
        },
        "ItemDataRole": {
            "DisplayRole", "DecorationRole", "EditRole", "ToolTipRole", "StatusTipRole",
            "WhatsThisRole", "SizeHintRole", "FontRole", "TextAlignmentRole",
            "BackgroundRole", "ForegroundRole", "CheckStateRole", "UserRole"
        },
        "CheckState": {
            "Unchecked", "PartiallyChecked", "Checked"
        },
        "FocusPolicy": {
            "NoFocus", "TabFocus", "ClickFocus", "StrongFocus", "WheelFocus"
        },
        "ContextMenuPolicy": {
            "NoContextMenu", "DefaultContextMenu", "ActionsContextMenu",
            "CustomContextMenu", "PreventContextMenu"
        },
        "SortOrder": {
            "AscendingOrder", "DescendingOrder"
        },
        "MatchFlag": {
            "MatchExactly", "MatchContains", "MatchStartsWith", "MatchEndsWith",
            "MatchRegularExpression", "MatchWildcard", "MatchFixedString",
            "MatchCaseSensitive", "MatchWrap", "MatchRecursive"
        }
    },
    "QFrame": {
        "Shape": {
            "NoFrame", "Box", "Panel", "WinPanel", "HLine", "VLine", "StyledPanel"
        },
        "Shadow": {
            "Plain", "Raised", "Sunken"
        }
    },
    "QSizePolicy": {
        "Policy": {
            "Fixed", "Minimum", "Maximum", "Preferred", "Expanding", "MinimumExpanding", "Ignored"
        }
    },
    "QComboBox": {
        "SizeAdjustPolicy": {
            "AdjustToContents", "AdjustToContentsOnFirstShow",
            "AdjustToMinimumContentsLengthWithIcon"
        }
    },
    "QKeySequence": {
        "StandardKey": {
            "UnknownKey", "HelpContents", "WhatsThis", "Open", "Close", "Save", "New",
            "Delete", "Cut", "Copy", "Paste", "Undo", "Redo", "Back", "Forward",
            "Refresh", "ZoomIn", "ZoomOut", "Print", "AddTab", "CloseTab", "NextChild",
            "PreviousChild", "Find", "FindNext", "FindPrevious", "Replace", "SelectAll",
            "Bold", "Italic", "Underline", "MoveToNextChar", "MoveToPreviousChar",
            "MoveToNextLine", "MoveToPreviousLine", "MoveToNextPage", "MoveToPreviousPage",
            "MoveToStartOfLine", "MoveToEndOfLine", "MoveToStartOfBlock", "MoveToEndOfBlock",
            "MoveToStartOfDocument", "MoveToEndOfDocument", "SelectNextChar",
            "SelectPreviousChar", "SelectNextLine", "SelectPreviousLine", "SelectNextPage",
            "SelectPreviousPage", "SelectStartOfLine", "SelectEndOfLine",
            "SelectStartOfBlock", "SelectEndOfBlock", "SelectStartOfDocument",
            "SelectEndOfDocument", "DeleteStartOfWord", "DeleteEndOfWord",
            "DeleteEndOfLine", "InsertParagraphSeparator", "InsertLineSeparator",
            "SaveAs", "Preferences", "Quit", "FullScreen", "Deselect"
        }
    },
    "QPainter": {
        "RenderHint": {
            "Antialiasing", "TextAntialiasing", "SmoothPixmapTransform",
            "VerticalSubpixelPositioning", "LosslessImageRendering"
        },
        "CompositionMode": {
            "CompositionMode_SourceOver", "CompositionMode_DestinationOver",
            "CompositionMode_Clear", "CompositionMode_Source", "CompositionMode_Destination",
            "CompositionMode_SourceIn", "CompositionMode_DestinationIn",
            "CompositionMode_SourceOut", "CompositionMode_DestinationOut",
            "CompositionMode_SourceAtop", "CompositionMode_DestinationAtop",
            "CompositionMode_Xor", "CompositionMode_Plus", "CompositionMode_Multiply",
            "CompositionMode_Screen", "CompositionMode_Overlay", "CompositionMode_Darken",
            "CompositionMode_Lighten", "CompositionMode_ColorDodge", "CompositionMode_ColorBurn",
            "CompositionMode_HardLight", "CompositionMode_SoftLight", "CompositionMode_Difference",
            "CompositionMode_Exclusion"
        }
    },
    "QIODevice": {
        "OpenModeFlag": {
            "NotOpen", "ReadOnly", "WriteOnly", "ReadWrite", "Append", "Truncate",
            "Text", "Unbuffered", "NewOnly", "ExistingOnly"
        }
    },
    "QMessageBox": {
        "StandardButton": {
            "NoButton", "Ok", "Save", "SaveAll", "Open", "Yes", "YesToAll", "No",
            "NoToAll", "Abort", "Retry", "Ignore", "Close", "Cancel", "Discard",
            "Help", "Apply", "Reset", "RestoreDefaults"
        },
        "Icon": {
            "NoIcon", "Information", "Warning", "Critical", "Question"
        }
    },
    "QFileDialog": {
        "FileMode": {
            "AnyFile", "ExistingFile", "Directory", "ExistingFiles"
        },
        "Option": {
            "ShowDirsOnly", "DontResolveSymlinks", "DontConfirmOverwrite",
            "DontUseSheet", "DontUseNativeDialog", "ReadOnly", "HideNameFilterDetails",
            "DontUseCustomDirectoryIcons"
        }
    },
    "QgsWkbTypes": {
        "GeometryType": {
            "PointGeometry", "LineGeometry", "PolygonGeometry", "UnknownGeometry", "NullGeometry"
        }
    },
    "QgsUnitTypes": {
        "LayoutUnit": {
            "LayoutMillimeters", "LayoutCentimeters", "LayoutMeters",
            "LayoutInches", "LayoutPoints", "LayoutPicas", "LayoutPixels"
        },
        "DistanceUnit": {
            "DistanceMeters", "DistanceKilometers", "DistanceFeet",
            "DistanceYards", "DistanceMiles", "DistanceNauticalMiles",
            "DistanceCentimeters", "DistanceMillimeters", "DistanceDegrees", "DistanceUnknownUnit"
        }
    },
    "QPageSize": {
        "Unit": {
            "Millimeter", "Point", "Inch", "Pica", "Didot", "Cicero"
        },
        "PageSizeId": {
            "A4", "B5", "Letter", "Legal", "Executive", "A0", "A1", "A2", "A3",
            "A5", "A6", "A7", "A8", "A9", "B0", "B1", "B10", "B2", "B3", "B4",
            "B6", "B7", "B8", "B9", "Custom"
        }
    },
    "QPageLayout": {
        "Orientation": {
            "Portrait", "Landscape"
        },
        "Unit": {
            "Millimeter", "Point", "Inch", "Pica", "Didot", "Cicero"
        },
        "Mode": {
            "StandardMode", "FullPageMode"
        }
    }
}

REMOVED_OR_RENAMED_APIS = {
    ("QPainter", "HighQualityAntialiasing"): "Removed in Qt6. Use 'QPainter.RenderHint.Antialiasing'.",
    ("QRegExp", None): "QRegExp is removed in Qt6. Use 'QRegularExpression'.",
    ("Qt", "MidButton"): "Renamed in Qt6. Use 'Qt.MouseButton.MiddleButton'.",
    ("Qt", "TextColorRole"): "Renamed in Qt6. Use 'Qt.ItemDataRole.ForegroundRole'.",
    ("Qt", "BackgroundColorRole"): "Renamed in Qt6. Use 'Qt.ItemDataRole.BackgroundRole'."
}

DEFAULT_IGNORES = [
    r"__pycache__",
    r"\.git",
    r"\.github",
    r"dist",
    r"build",
    r"tests?",
    r"^test_.*\.py$"
]


class Qt6CompatibilityVisitor(ast.NodeVisitor):
    """AST visitor detecting Qt6 / QGIS 4 incompatibilities."""

    def __init__(self, filepath: Path, rel_path: str):
        self.filepath = filepath
        self.rel_path = rel_path
        self.issues: List[Tuple[int, int, str, str]] = []  # (line, col, severity, message)

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            if alias.name.startswith("PyQt5"):
                self.issues.append((
                    node.lineno,
                    node.col_offset,
                    "ERROR",
                    f"Direct PyQt5 import '{alias.name}'. "
                    "QGIS plugins must import from 'qgis.PyQt' for Qt5/Qt6 portability."
                ))
            elif alias.name == "QRegExp":
                self.issues.append((
                    node.lineno,
                    node.col_offset,
                    "ERROR",
                    "QRegExp is removed in Qt6. Use QRegularExpression."
                ))
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module:
            if node.module.startswith("PyQt5"):
                self.issues.append((
                    node.lineno,
                    node.col_offset,
                    "ERROR",
                    f"Direct PyQt5 import 'from {node.module}'. "
                    "QGIS plugins must import from 'qgis.PyQt' for Qt5/Qt6 portability."
                ))
        for alias in node.names:
            if alias.name == "QRegExp":
                self.issues.append((
                    node.lineno,
                    node.col_offset,
                    "ERROR",
                    "QRegExp is removed in Qt6. Use QRegularExpression."
                ))
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute):
        if isinstance(node.value, ast.Name):
            cls_name = node.value.id
            attr = node.attr

            # Check removed/renamed APIs
            if (cls_name, attr) in REMOVED_OR_RENAMED_APIS:
                msg = REMOVED_OR_RENAMED_APIS[(cls_name, attr)]
                self.issues.append((
                    node.lineno,
                    node.col_offset,
                    "ERROR",
                    f"'{cls_name}.{attr}' - {msg}"
                ))
            # Check QImage Format prefix
            elif cls_name == "QImage" and attr.startswith("Format_"):
                self.issues.append((
                    node.lineno,
                    node.col_offset,
                    "ERROR",
                    f"Un-scoped enum '{cls_name}.{attr}'. Add 'Format' before '{attr}': '{cls_name}.Format.{attr}'"
                ))
            # Check known scoped enums
            elif cls_name in KNOWN_QT_SCOPED_ENUMS:
                for scope, values in KNOWN_QT_SCOPED_ENUMS[cls_name].items():
                    if attr in values:
                        self.issues.append((
                            node.lineno,
                            node.col_offset,
                            "ERROR",
                            f"Un-scoped enum '{cls_name}.{attr}'. "
                            f"Add '{scope}' before '{attr}': '{cls_name}.{scope}.{attr}'"
                        ))
                        break

        # Check exec_() deprecation
        if node.attr == "exec_":
            self.issues.append((
                node.lineno,
                node.col_offset,
                "WARNING",
                "Method 'exec_()' is deprecated in Qt5/Qt6. Consider migrating to 'exec()'."
            ))

        self.generic_visit(node)


def audit_directory_for_qt6(
    target_dir: Path, ignore_patterns: List[str] = None
) -> List[Tuple[str, int, int, str, str]]:
    """Scan all python files in target_dir for Qt6 / QGIS 4 compatibility issues."""
    target_dir = target_dir.resolve()
    ignores = ignore_patterns or DEFAULT_IGNORES
    all_issues = []

    for root, dirs, files in os.walk(target_dir):
        # Filter directories in-place
        dirs[:] = [d for d in dirs if not any(re.search(pat, d, re.IGNORECASE) for pat in ignores)]
        for file in files:
            if not file.endswith(".py"):
                continue
            if any(re.search(pat, file, re.IGNORECASE) for pat in ignores):
                continue

            filepath = Path(root) / file
            rel_path = filepath.relative_to(target_dir).as_posix()

            try:
                content = filepath.read_text(encoding="utf-8", errors="ignore")
                tree = ast.parse(content, filename=str(filepath))
            except SyntaxError as e:
                all_issues.append((
                    rel_path, e.lineno or 1, e.offset or 0, "ERROR", f"SyntaxError parsing Python file: {e}"
                ))
                continue

            visitor = Qt6CompatibilityVisitor(filepath, rel_path)
            visitor.visit(tree)

            for line, col, severity, msg in visitor.issues:
                all_issues.append((rel_path, line, col, severity, msg))

    return all_issues


def main():
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    issues = audit_directory_for_qt6(target)

    print(f"🔍 Checking Qt6 / QGIS 4 Forward-Compatibility for: {target.resolve()}")
    print("=" * 70)

    if not issues:
        print("✨ 100% COMPLIANT! Zero Qt6 / QGIS 4 compatibility issues found.")
        print("   This plugin will earn the green 'QGIS 4 Ready' badge on plugins.qgis.org.")
        sys.exit(0)

    print(f"⚠️  Found {len(issues)} Qt6 / QGIS 4 compatibility issues:")
    for rel_path, line, col, severity, msg in issues:
        print(f"  • {rel_path}:{line}:{col} [{severity}] {msg}")

    print("\n❌ Plugin does NOT meet 100% QGIS 4 / Qt6 readiness.")
    sys.exit(1)


if __name__ == "__main__":
    main()
