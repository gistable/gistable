# ClojureHelpers.py for Sublime Text 3
# originally by James MacCaulley
# https://gist.github.com/jamesmacaulay/5457344

import re
import sublime
import sublime_plugin
import SublimeREPL.sublimerepl
import SublimeREPL.text_transfer

class RefreshNamespacesInReplCommand(SublimeREPL.text_transfer.ReplTransferCurrent):
  def run(self, edit):
    text = "(clojure.tools.namespace.repl/refresh)"
    self.view.window().run_command("repl_send", {"external_id": self.repl_external_id(), "text": text})

class SwitchToCurrentNamespaceInReplCommand(SublimeREPL.text_transfer.ReplTransferCurrent):
  def run(self, edit):
    if SublimeREPL.sublimerepl.manager.repl_view(self.view):
      return
    ns = re.sub("ns\s*", "", self.view.substr(self.view.find("ns\s*\S+",0)))
    text = "(in-ns '" + ns + ")"
    self.view.window().run_command("repl_send", {"external_id": self.repl_external_id(), "text": text})

class RunAllClojureTestsFromProjectInReplCommand(SublimeREPL.text_transfer.ReplTransferCurrent):
  def run(self, edit):
    form = "(do (clojure.tools.namespace.repl/refresh) (apply clojure.test/run-tests (clojure.tools.namespace.find/find-namespaces-in-dir (clojure.java.io/file \"test\"))))"
    self.view.window().run_command("refresh_namespaces_in_repl")
    self.view.window().run_command("repl_send", {"external_id": self.repl_external_id(), "text": form})

class RunClojureTestsFromCurrentNamespaceInReplCommand(SublimeREPL.text_transfer.ReplTransferCurrent):
  def run(self, edit):
    if SublimeREPL.sublimerepl.manager.repl_view(self.view):
      return
    ns = re.sub("ns\s*", "", self.view.substr(self.view.find("ns\s*\S+",0)))

    default_test_ns = re.sub("(.*)(?<!-test)\\Z","\\1-test", ns, 1)
    alt_style_test_ns = re.sub("\A([^\\.]*\\.)(?!test)","\\1test.", ns, 1)
    form = "(try (clojure.test/run-tests '" + default_test_ns + ")\n  (catch Exception e\n    (clojure.test/run-tests '" + alt_style_test_ns + ")))"
    self.view.window().run_command("refresh_namespaces_in_repl")
    self.view.window().run_command("repl_send", {"external_id": self.repl_external_id(), "text": form})
