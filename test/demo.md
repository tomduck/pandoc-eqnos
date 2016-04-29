
$$ y = f(x) $$ {#eq:1}

$$ y = g(x) $${#eq:2}

Equations {@eq:1} and @eq:2, Eqs. {@eq:1}-{@eq:3} and Eqs. {@eq:1}-{@eq:2}-{@eq:3}.

Equations and references in lists:

  * Equation {@eq:3}:
    $$ y = h(x) $$ {#eq:3}
  * Equations {@eq:1} and @eq:2, Eqs. {@eq:1}-{@eq:3} and 
    Eqs. {@eq:1}-{@eq:2}-{@eq:3}.

Equations @eq:4 and @eq:5 are tagged equations (with and without quotes, respectively):

$$ y = F(x) $$ {#eq:4 tag="B.1"}

$$ y = G(x) $$ {#eq:5 tag=B.2}

@eq:6 has a single-quoted tag with space:
$$ y = H(x) $$ {#eq:6 tag='Eq. B.3'}
Equation @eq:7 has a primed tag:
$$ y = H'(x) $$ {#eq:7 tag="$\mathrm{B.3'}$"}

Here is an unreferenceable numbered equation:

$$ E = mc^2 $$ {#eq:}

A [regular link](http://example.com/), an [*italicized link*](http://example.com/) and an email.address@mailinator.com.


\newpage


--------------------------------------------------------------------

Corner Cases
------------

Below is an equation with empty attributes.  It shouldn't be numbered.

$$ E = mc^2 $$ {}


****


Below is an equation with no attributes.  It shouldn't be numbered.

$$ E = mc^2 $$


****


Here is a series of unreferenceable equations:

$$ y = F(x) $$ {#eq:}

$$ y = G(x) $$ {#eq:}

$$ y = H(x) $$ {#eq:}
