# Implementation Plan: Complete API Routes

## Overview

This plan outlines the tasks to complete and correct the API routes in rhBackFast. The implementation will fix syntax errors, add missing imports, and ensure all routes have consistent pagination and expansion support.

## Tasks

- [x] 1. Fix imports and syntax errors
  - Add missing `func` import from SQLAlchemy
  - Fix syntax errors in contrat_router section
  - Fix syntax errors in user_router section
  - Verify all imports are correct
  - _Requirements: 1.1, 1.2, 1.3_

- [x] 2. Verify or create query utilities
  - Check if `app/core/query_utils.py` exists
  - If missing, create `parse_expand_param` function
  - If missing, create `apply_expansion` function
  - Test utility functions work correctly
  - _Requirements: 3.2, 3.3_

- [x] 3. Fix Service routes
  - Ensure GET /services has proper pagination
  - Ensure GET /services has expand support
  - Ensure GET /services/{id} has expand support
  - Verify POST, PUT, DELETE routes are complete
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 4. Fix Group routes
  - Ensure GET /groups has proper pagination
  - Ensure GET /groups has expand support
  - Ensure GET /groups/{id} has expand support
  - Verify POST, PUT, DELETE routes are complete
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 5. Fix ServiceGroup routes
  - Ensure GET /service-groups has proper pagination
  - Ensure GET /service-groups has expand support
  - Ensure GET /service-groups/{id} has expand support
  - Verify POST, PUT, DELETE routes are complete
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 6. Fix User routes
  - Fix syntax errors in user_router
  - Ensure GET /users has proper pagination
  - EnsureGET /users has expand support
  - Ensure GET /users/{id} has expand support
  - Verify POST, PUT, DELETE routes are complete
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 7. Fix UserGroup routes
  - Ensure GET /user-groups has proper pagination
  - Ensure GET /user-groups has expand support
  - Ensure GET /user-groups/{id} has expand support
  - Verify POST, PUT, DELETE routes are complete
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 8. Fix Permission routes
  - Ensure GET /permissions has proper pagination
  - Ensure GET /permissions has expand support
  - Ensure GET /permissions/{id} has expand support
  - Add POST /permissions route if needed
  - _Requirements: 9.1, 9.2, 9.3_

- [x] 9. Fix GroupPermission routes
  - Ensure GET /group-permissions has proper pagination
  - Ensure GET /group-permissions has expand support
  - Verify POST, PUT, DELETE routes are complete
  - _Requirements: 10.1, 10.2, 10.3, 10.4_

- [x] 10. Fix Employe routes
  - Ensure GET /employees has proper pagination
  - Ensure GET /employees has expand support
  - Ensure GET /employees/{id} has expand support
  - Verify POST, PUT, DELETE routes are complete
  - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_

- [x] 11. Fix Contrat routes
  - Fix syntax errors in contrat_router
  - Ensure GET /contracts has proper pagination
  - Ensure GET /contracts has expand support
  - Ensure GET /contracts/{id} has expand support
  - Verify POST, PUT, DELETE routes are complete
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

- [x] 12. Fix Document routes
  - Ensure GET /documents has proper pagination
  - Ensure GET /documents has expand support
  - Ensure GET /documents/{id} has expand support
  - Verify POST, PUT, DELETE routes are complete
  - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5_

- [x] 13. Checkpoint - Verify syntax and run basic tests
  - Run syntax checker on routes.py
  - Ensure application starts without errors
  - Test a few endpoints manually
  - Ask user if questions arise

- [ ]* 14. Write unit tests for pagination
  - [ ]* 14.1 Test pagination with default parameters
    - Test skip=0, limit=100 returns correct structure
    - _Requirements: 2.1, 2.2_

  - [ ]* 14.2 Test pagination with custom parameters
    - Test various skip/limit combinations
    - _Requirements: 2.2_

  - [ ]* 14.3 Test no_pagination flag
    - Test no_pagination=true returns all results
    - _Requirements: 2.3_

- [ ]* 15. Write unit tests for expand functionality
  - [ ]* 15.1 Test expand parameter parsing
    - Test single relation expansion
    - Test multiple relations expansion
    - _Requirements: 3.1, 3.2_

  - [ ]* 15.2 Test expand application
  - Test relations are loaded correctly
    - _Requirements: 3.3, 3.4, 3.5_

- [ ]* 16. Write property-based tests
  - [ ]* 16.1 Property test for pagination consistency
    - **Property 2: Pagination Consistency**
    - **Validates: Requirements 2.1, 2.2, 2.4**

  - [ ]* 16.2 Property test for no pagination response
    - **Property 3: No Pagination Response**
    - **Validates: Requirements 2.3, 2.5**

  - [ ]* 16.3 Property test for expand application
    - **Property 4: Expand Application**
    - **Validates: Requirements 3.1, 3.3, 3.4, 3.5**

  - [ ]* 16.4 Property test for route completeness
    - **Property 5: Route Completeness**
    - **Validates: Requirements 4-13**

- [ ] 17. Final checkpoint - Run all tests
  - Run all unit tests
  - Run all property-based tests
  - Verify all routes work correctly
  - Ask user for final review

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases

