<?php

final class DefaultLintEngine extends ArcanistLintEngine {
  private $static_file_regexp = array(
    "^(M|m)akefile$",
    "\.min\.(js|css)$",
    "\.json$",
    "^db.sqlite3$",
  );
  public function buildLinters() {

    // This is a list of paths which the user wants to lint. Either they
    // provided them explicitly, or arc figured them out from a commit or set
    // of changes. The engine needs to return a list of ArcanistLinter objects,
    // representing the linters which should be run on these files.
    $paths = $this->getPaths();

    // Linters are responsible for actually analyzing the contents of a file
    // and raising warnings and errors.
    $python_linter = new ArcanistPyLintLinter();
    $js_linter = new ArcanistJSHintLinter();
    $file_linter = new ArcanistTextLinter();

    // Remove any paths that don't exist before we add paths to linters. We want
    // to do this for linters that operate on file contents because the
    // generated list of paths will include deleted paths when a file is
    // removed.
    foreach ($paths as $key => $path) {
      if (!$this->pathExists($path)) {
        unset($paths[$key]);
      }
    }

    /*
    $file_linter->setPaths($paths);
    $python_linter->setPaths(preg_grep('/\.py$/', $paths));
    $js_linter->setPaths(preg_grep('/\.js$/', $paths));
     */

    foreach ($paths as $path) {
      if (preg_match('@/static/.*/img/@', $path)) {
        continue;
      }
      if (preg_match('@/externals/@', $path)) {
        continue;
      }

      // whitespace
      $match = "/(" . implode("|",$this->static_file_regexp) . ")/";
      if (!preg_match($match, $path)) {
        $file_linter->addPath($path);
      }

      // python
      if (preg_match('/\.py$/', $path)
        && !preg_match('/\/xhpy\//', $path)
        && !preg_match('/views.py$/', $path)) {
        $python_linter->addPath($path);
      }

      // javascript
      if (preg_match('/\.js$/', $path) && !preg_match('/\.min\.js$/', $path)) {
        $js_linter->addPath($path);
      }
    }

    return array(
      $python_linter,
      $js_linter,
      $file_linter,
    );
  }

}
