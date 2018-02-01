class BaseModelView(ModelView):
    list_template = 'admin/model_list.html'
    
    export_columns = None
    
    # Exporting
    def _get_data_for_export(self):
        view_args = self._get_list_extra_args()

        # Map column index to column name
        sort_column = self._get_column_by_idx(view_args.sort)
        if sort_column is not None:
            sort_column = sort_column[0]

        _, query = self.get_list(view_args.page, sort_column, view_args.sort_desc, view_args.search,
                                 view_args.filters, execute=False)

        return query.limit(None).all()

    def get_export_csv(self):
        self.export_columns = self.export_columns or [column_name for column_name, _ in self._list_columns]

        io = StringIO()
        rows = csv.DictWriter(io, self.export_columns)

        data = self._get_data_for_export()

        rows.writeheader()

        for item in data:
            row = {column: unicode(rec_getattr(item, column)).encode('utf-8') for column in self.export_columns}
            rows.writerow(row)

        io.seek(0)
        return io.getvalue()

    @expose('/export/')
    def export(self):
        response = make_response(self.get_export_csv())
        response.mimetype = 'text/csv'
        response.headers['Content-Disposition'] = 'attachment; filename=%s.csv' % self.name.lower().replace(' ', '_')

        return response