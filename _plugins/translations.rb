# Side-by-side translations.
#
# Posts and pages carry their language as a filename suffix:
#
#   _posts/2024/2024-07-27-headquarters.pl.md
#   _posts/2024/2024-07-27-headquarters.en.md
#   about.pl.md, about.en.md
#
# This hook (runs after Jekyll reads the site, before polyglot coordinates
# languages):
# - sets `lang` from the suffix and strips it from post slugs, so URLs don't
#   change;
# - lets translations inherit the shared front matter from the default-language
#   original (`date` always; `categories`, `header`, `last_modified_at` unless
#   the translation sets them);
# - warns about default-language posts without a translation, unless they are
#   marked with `lang-exclusive`.
module Translations
  SUFFIX = %r!\.([a-z]{2})\z!.freeze
  INHERITED_FIELDS = %w(categories header last_modified_at).freeze

  def self.split(name)
    match = name.match(SUFFIX)
    match ? [name.sub(SUFFIX, ""), match[1]] : [name, nil]
  end

  def self.blank?(value)
    value.nil? || (value.respond_to?(:empty?) && value.empty?)
  end
end

Jekyll::Hooks.register :site, :post_read do |site|
  languages = site.config["languages"] || []
  default_lang = site.config["default_lang"]

  groups = Hash.new { |hash, key| hash[key] = {} }
  site.posts.docs.each do |doc|
    stem, lang = Translations.split(doc.data["slug"].to_s)
    next unless lang && languages.include?(lang)

    doc.data["slug"] = stem
    doc.data["lang"] ||= lang
    groups[Translations.split(doc.basename_without_ext).first][lang] = doc
  end

  groups.each_value do |docs|
    original = docs[default_lang]
    next unless original

    docs.each do |lang, doc|
      next if lang == default_lang

      doc.data["date"] = original.data["date"]
      Translations::INHERITED_FIELDS.each do |field|
        doc.data[field] = original.data[field] if Translations.blank?(doc.data[field])
      end
    end

    # Polyglot reads the site once per language; report only once.
    next unless site.config["active_lang"].nil? || site.config["active_lang"] == default_lang
    next unless original.data["lang-exclusive"].nil?

    (languages - docs.keys).each do |lang|
      Jekyll.logger.warn "Translations:", "#{original.relative_path} has no #{lang} translation"
    end
  end

  site.pages.each do |page|
    _, lang = Translations.split(File.basename(page.name, page.ext))
    page.data["lang"] ||= lang if lang && languages.include?(lang)
  end
end
