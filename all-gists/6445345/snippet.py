(defn y-combinator [f]
  (#(% %) (fn [x] (f #(apply (x x) %&)))))

((y-combinator
  (fn [fab]
    #(if (zero? %) 1 (* % (fab (dec %))))))
 10)