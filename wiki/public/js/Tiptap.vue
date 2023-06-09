<script setup>
import H2Icon from "./icons/h-2.vue";
import LinkIcon from "./icons/link.vue";
import BoldIcon from "./icons/bold.vue";
import ItalicIcon from "./icons/italic.vue";
import TableIcon from "./icons/table-2.vue";
import CodeViewIcon from "./icons/code-view.vue";
import HorizontalRule from "./icons/separator.vue"
import AlignLeftIcon from "./icons/align-left.vue";
import AlignRightIcon from "./icons/align-right.vue";
import AlignCenterIcon from "./icons/align-center.vue";
import ListOrderedIcon from "./icons/list-ordered.vue";
import BlockquoteIcon from "./icons/double-quotes-r.vue";
import ImageAddLineIcon from "./icons/image-add-line.vue";
import ListUnorderedIcon from "./icons/list-unordered.vue";
</script>

<template>
  <div>
  <div v-if="editor">
    <div class="wiki-edit-controls">
      <div class="dropdown">
        <button class="dropdown-toggle" type="button" id="dropdownMenuButton" data-toggle="dropdown" aria-haspopup="true"
          aria-expanded="false">
          <H2Icon />
        </button>
        <div class="dropdown-menu" aria-labelledby="headingDropdownMenuButton">
          <a class="dropdown-item" @click="editor.chain().focus().toggleHeading({ level: 2 }).run()"
            :class="{ 'is-active': editor.isActive('heading', { level: 2 }) }">
            Heading 2
          </a>
          <a class="dropdown-item" @click="editor.chain().focus().toggleHeading({ level: 3 }).run()"
            :class="{ 'is-active': editor.isActive('heading', { level: 3 }) }">
            Heading 3
          </a>
          <a class="dropdown-item" @click="editor.chain().focus().toggleHeading({ level: 4 }).run()"
            :class="{ 'is-active': editor.isActive('heading', { level: 4 }) }">
            Heading 4
          </a>
          <a class="dropdown-item" @click="editor.chain().focus().toggleHeading({ level: 5 }).run()"
            :class="{ 'is-active': editor.isActive('heading', { level: 5 }) }">
            Heading 5
          </a>
          <a class="dropdown-item" @click="editor.chain().focus().toggleHeading({ level: 6 }).run()"
            :class="{ 'is-active': editor.isActive('heading', { level: 6 }) }">
            Heading 6
          </a>
        </div>
      </div>
      <div class="vertical-sep"></div>
      <button @click="editor.chain().focus().toggleBold().run()"
        :disabled="!editor.can().chain().focus().toggleBold().run()" :class="{ 'is-active': editor.isActive('bold') }">
        <BoldIcon />
      </button>
      <button @click="editor.chain().focus().toggleItalic().run()"
        :disabled="!editor.can().chain().focus().toggleItalic().run()"
        :class="{ 'is-active': editor.isActive('italic') }">
        <ItalicIcon />
      </button>
      <div class="vertical-sep"></div>
      <button @click="editor.chain().focus().toggleBulletList().run()"
        :class="{ 'is-active': editor.isActive('bulletList') }">
        <ListUnorderedIcon />
      </button>
      <button @click="editor.chain().focus().toggleOrderedList().run()"
        :class="{ 'is-active': editor.isActive('orderedList') }">
        <ListOrderedIcon />
      </button>
      <div class="vertical-sep"></div>
      <button @click="editor.chain().focus().setTextAlign('left').run()"
        :class="{ 'is-active': editor.isActive({ textAlign: 'left' }) }">
        <AlignLeftIcon />
      </button>
      <button @click="editor.chain().focus().setTextAlign('center').run()"
        :class="{ 'is-active': editor.isActive({ textAlign: 'center' }) }">
        <AlignCenterIcon />
      </button>
      <button @click="editor.chain().focus().setTextAlign('right').run()"
        :class="{ 'is-active': editor.isActive({ textAlign: 'right' }) }">
        <AlignRightIcon />
      </button>
      <div class="vertical-sep"></div>
      <button @click="addImage" :class="{ 'is-active': editor.isActive('image') }">
        <ImageAddLineIcon />
      </button>
      <button @click="openLinkDialog" :class="{ 'is-active': editor.isActive('link') }">
        <LinkIcon />
      </button>
      <div class="modal fade" id="linkModal" tabindex="-1" role="dialog" aria-labelledby="linkModal" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered" role="document">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title" id="linkModalTitle">Set Link</h5>
            </div>
            <div class="modal-body">
              <input type="text" id="link" name="link">
            </div>
            <div class="modal-footer">
              <button type="button" @click="setLink" class="btn btn-primary btn-sm" data-dismiss="modal">Add Link</button>
            </div>
          </div>
        </div>
      </div>
      <button @click="editor.chain().focus().toggleBlockquote().run()"
        :class="{ 'is-active': editor.isActive('blockquote') }">
        <BlockquoteIcon />
      </button>
      <button @click="editor.chain().focus().toggleCodeBlock().run()"
        :class="{ 'is-active': editor.isActive('codeBlock') }">
        <CodeViewIcon />
      </button>
      <button @click="editor.chain().focus().setHorizontalRule().run()">
        <HorizontalRule />
      </button>
      <div class="dropdown">
        <button class="dropdown-toggle" type="button" id="dropdownMenuButton" data-toggle="dropdown" aria-haspopup="true"
          aria-expanded="false">
          <TableIcon />
        </button>
        <div class="dropdown-menu" aria-labelledby="tableDropdownMenuButton">
          <a class="dropdown-item" @click="
            editor
              .chain()
              .focus()
              .insertTable({ rows: 3, cols: 3, withHeaderRow: true })
              .run()
          ">
            Insert Table
          </a>
          <a class="dropdown-item" @click="editor.chain().focus().addColumnBefore().run()">
            Add Column Before
          </a>
          <a class="dropdown-item" @click="editor.chain().focus().addColumnAfter().run()">
            Add Column After
          </a>
          <a class="dropdown-item" @click="editor.chain().focus().deleteColumn().run()">
            Delete Column
          </a>
          <a class="dropdown-item" @click="editor.chain().focus().addRowBefore().run()">
            Add Row Before
          </a>
          <a class="dropdown-item" @click="editor.chain().focus().addRowAfter().run()">
            Add Row After
          </a>
          <a class="dropdown-item" @click="editor.chain().focus().deleteRow().run()">
            Delete Row
          </a>
          <a class="dropdown-item" @click="editor.chain().focus().toggleHeaderColumn().run()">
            Toggle Header Column
          </a>
          <a class="dropdown-item" @click="editor.chain().focus().toggleHeaderRow().run()">
            Toggle Header Row
          </a>
          <a class="dropdown-item" @click="editor.chain().focus().toggleHeaderCell().run()">
            Toggle Header Cell
          </a>
          <a class="dropdown-item" @click="editor.chain().focus().deleteTable().run()">
            Delete Table
          </a>
        </div>
      </div>
    </div>
    <div class="wiki-edit-control-btn hide">
      <div class="btn btn-secondary discard-edit-btn btn-sm" :data-new="isEmptyEditor">Discard</div>
      <div class="btn-group">
        <div type="button" class="btn btn-primary save-wiki-page-btn btn-sm" @click="() => saveWikiPage()">Save</div>
        <div type="button" class="btn btn-primary btn-sm dropdown-toggle dropdown-toggle-split" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
          <span class="sr-only">Toggle Dropdown</span>
        </div>
        <div class="dropdown-menu">
          <a class="dropdown-item" @click="() => saveWikiPage()">Save</a>
          <a class="dropdown-item" @click="() => saveWikiPage(true)">Draft</a>
        </div>
      </div>
    </div>
  </div>
  <editor-content :editor="editor" />
  </div>
</template>

<script>
import { lowlight } from 'lowlight'
import Link from "@tiptap/extension-link";
import Image from "@tiptap/extension-image";
import Table from "@tiptap/extension-table";
import StarterKit from "@tiptap/starter-kit";
import Document from "@tiptap/extension-document";
import TableRow from "@tiptap/extension-table-row";
import TextAlign from "@tiptap/extension-text-align";
import TableCell from "@tiptap/extension-table-cell";
import { Editor, EditorContent, InputRule } from "@tiptap/vue-3";
import Placeholder from "@tiptap/extension-placeholder";
import TableHeader from "@tiptap/extension-table-header";
import CodeBlockLowlight from '@tiptap/extension-code-block-lowlight'

const CustomDocument = Document.extend({
  content: "heading block*",
});

export default {
  components: {
    EditorContent,
  },

  props: {
    isEmptyEditor: {
      type: Boolean,
      default: false
    },
  },

  data() {
    return {
      editor: null,
    };
  },

  mounted() {
    const disableMarkdownShortcut = (markdownShortcut, originalChar) => {
      return new InputRule(
        new RegExp(`(^|[\\s])${markdownShortcut}(?![\\w])`, 'g'),
        (state, match, start, end) => {
          const text = state.doc.textBetween(start, end)
          if (text === markdownShortcut) {
            return originalChar
          }
          return null
        }
      )
    }

    const getContent = () => {
      if (patchNewCode !== "<h1>{{ patch_new_title }}</h1>{{ patch_new_code }}") return patchNewCode
      else if (!this.isEmptyEditor) return $(".from-markdown").html().replaceAll(/<br class="ProseMirror-trailingBreak">/g, '')
      return "<h1></h1><p></p>"
    }

    this.editor = new Editor({
      extensions: [
        CustomDocument,
        StarterKit.configure({
          document: false,
          codeBlock: false,
        }),
        Placeholder.configure({
          placeholder: ({ node }) => {
            if (node.type.name === "heading" && node.attrs.level === 1) return "What’s the Wiki title?";
          },
        }),
        Link.configure({
          openOnClick: false,
        }),
        Image.configure({
          allowBase64: true,
          inline: true,
        }),
        Table,
        TableRow,
        TableHeader,
        TableCell,
        TextAlign.configure({
          types: ['heading', 'paragraph'],
        }),
        CodeBlockLowlight.configure({
          lowlight,
        }),
      ],
      inputRules: [disableMarkdownShortcut("#", "#")],
      content: getContent(),
    });
  },

  methods: {
    openLinkDialog() {
      $('#linkModal').modal();
      const previousUrl = this.editor.getAttributes("link").href;
      if (previousUrl) $("#linkModal #link").val(previousUrl)
      else $("#linkModal #link").val("")
    },
    setLink() {
      $('#linkModal').modal();
      const link = $("#linkModal #link").val()
      if (link === null) return;

      // empty
      if (link === "") {
        this.editor.chain().focus().extendMarkRange("link").unsetLink().run();
        return;
      }

      // update link
      this.editor.chain().focus().extendMarkRange("link").setLink({ href: link }).run();
    },
    addImage() {
      const input = document.createElement('input');
      input.type = 'file';

      input.onchange = e => {
        const file = e.target.files[0];
        const reader = new FileReader();
        reader.readAsDataURL(file);

        reader.onload = readerEvent => {
          const content = readerEvent.target.result;
          if (content) {
            this.editor.chain().focus().setImage({ src: content }).run()
          }
        }
      }
      input.click();
    },
    saveWikiPage(draft=false) {
      const urlParams = new URLSearchParams(window.location.search);
      const title = $(`.${this.isEmptyEditor ? 'new-' : ''}wiki-editor .ProseMirror h1`).html();
      // markdown=1 tag is needed for older wiki content to properly render
      const content = `<div markdown="1">${$(`.${this.isEmptyEditor ? 'new-' : ''}wiki-editor .ProseMirror`).html().replace(/<h1>.*?<\/h1>/, '')}</div>`;

      dontmanage.call({
        method: "wiki.wiki.doctype.wiki_page.wiki_page.update",
        args: {
          name: $('[name="wiki-page-name"]').val(),
          message: `${this.isEmptyEditor ? 'Created' : 'Edited'} ${title}`,
          content,
          new: this.isEmptyEditor,
          new_sidebar_items: this.isEmptyEditor ? getSidebarItems() : '',
          title,
          draft,
          new_sidebar_group: this.isEmptyEditor ? urlParams.get("newWiki"): "",
          wiki_page_patch: urlParams.get("wikiPagePatch")
        },
        callback: (r) => {
          // route back to the main page
          window.location.href = "/" + r.message.route;
        },
        freeze: true,
      });
    }
  },

  beforeUnmount() {
    this.editor.destroy();
  },
};
</script>
