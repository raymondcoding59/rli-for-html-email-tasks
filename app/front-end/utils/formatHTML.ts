import prettier from "prettier/standalone"
import htmlParser from "prettier/plugins/html"

export async function formatHTML(code: string) {

  return prettier.format(code, {
    parser: "html",
    plugins: [htmlParser],
    tabWidth: 2,
    printWidth: 100
  })
}